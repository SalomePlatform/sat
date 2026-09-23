#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2024  CEA/DEN
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.

"""
Windows MSI installer builder for SAT (``sat package <app> --build_msi``).

This module is **generic**: it knows nothing about SALOME specifically.
Everything project-specific (the WiX ``Package.wxs`` feature tree, branding,
launchers, the product -> ComponentGroup map, product exclusions, staging
fixes) is provided by the *project* through an ``installer`` section in the
application configuration. For SALOME these resources live in
``sat_salome/installer/windows/``.

Pipeline (mirrors a hand-written WiX build):

    application install tree (APPLICATION.workdir: W64/, env_launch.bat, salome)
        + project installer resources (launchers, scripts, branding, *.wxs)
            --> staging directory
                --> optional project pre_build script (runtime staging fixes)
                    --> generate w64_files.wxs (one Component per directory)
                        --> wix build Package.wxs [extra .wxs] w64_files.wxs
                            --> <output>.msi

One ``<Component>`` per directory (not per file) keeps the component count
well under MSI's 65 536 limit for install trees with 100 000+ files.
"""

import os
import stat
import shutil
import hashlib
import uuid
import io
import subprocess

import src
import src.debug as DBG


def _on_rm_error(func, path, exc_info):
    """rmtree onerror handler: clear read-only attribute then retry (Windows)."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def _rmtree_force(path):
    """Remove a directory tree even if it contains read-only files."""
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=_on_rm_error)


def _remove_file_force(path):
    """Remove a file even if it is read-only."""
    if os.path.isfile(path):
        try:
            os.chmod(path, stat.S_IWRITE)
        except OSError:
            pass
        os.remove(path)


# ---------------------------------------------------------------------------
# Config access helpers
# ---------------------------------------------------------------------------

def _get(cfg, key, default=None):
    """Safe attribute/key access on a pyconf node."""
    try:
        if key in cfg:
            return cfg[key]
    except Exception:
        pass
    return default


def _as_list(node):
    """Return a pyconf list (or scalar) as a plain python list of str."""
    if node is None:
        return []
    try:
        return [str(x) for x in node]
    except TypeError:
        return [str(node)]


def _find_installer_cfg(config):
    """Locate the 'installer' section.

    Looked up first on the application (APPLICATION.installer, an app-specific
    override), then on any loaded project (PROJECTS.projects.<name>.installer)
    so a single definition can be shared by all the project's applications.
    """
    app_installer = _get(config.APPLICATION, "installer")
    if app_installer is not None:
        return app_installer
    projects = _get(config, "PROJECTS")
    projects = _get(projects, "projects") if projects is not None else None
    if projects is not None:
        for name in projects:
            inst = _get(projects[name], "installer")
            if inst is not None:
                return inst
    return None


def _as_dict(node):
    """Return a pyconf mapping as a plain python dict {str: str}."""
    d = {}
    if node is None:
        return d
    try:
        for k in node:
            d[str(k)] = str(node[k])
    except Exception:
        pass
    return d


# ---------------------------------------------------------------------------
# WiX source generation (install tree -> .wxs, one Component per directory)
# ---------------------------------------------------------------------------

def sanitize_id(path):
    """Convert a relative path to a valid WiX identifier ([A-Za-z_][A-Za-z0-9_.]*, <=72)."""
    if not path:
        return "root"
    s = path.replace(os.sep, ".").replace("/", ".")
    s = "".join(c if c.isalnum() or c == "." else "_" for c in s)
    if s[0].isdigit():
        s = "_" + s
    if len(s) > 62:
        h = hashlib.md5(path.encode()).hexdigest()[:8]
        s = s[:53] + "_" + h
    return s


def _make_guid(namespace, rel_path):
    """Deterministic GUID from a relative path (stable across rebuilds)."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS,
                          namespace + "/" + rel_path.replace(os.sep, "/")))


def _xml_escape(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def _collect_tree(source_dir, spec):
    """Walk the staged tree, returning {rel_dir: [files]} and {rel_dir: group}.

    ``spec`` carries the project rules:
      root_install_files, install_dirs, skip_dirs, skip_products,
      product_root, product_groups.
    """
    root_files_wl = set(spec["root_install_files"])
    install_dirs = spec["install_dirs"]
    skip_dirs = set(spec["skip_dirs"])
    skip_products = set(spec["skip_products"])
    product_root = spec["product_root"]
    product_groups = spec["product_groups"]

    tree = {}
    dir_groups = {}

    # Whitelisted root files
    root_files = [f for f in sorted(os.listdir(source_dir))
                  if os.path.isfile(os.path.join(source_dir, f)) and f in root_files_wl]
    if root_files:
        tree[""] = root_files
        dir_groups[""] = "CG_root"

    # Whitelisted top-level directories, walked recursively
    for dirname in sorted(install_dirs):
        dirpath = os.path.join(source_dir, dirname)
        if not os.path.isdir(dirpath):
            continue
        for walk_dir, subdirs, filenames in os.walk(dirpath):
            if dirname == product_root:
                rel_to_root = os.path.relpath(walk_dir, os.path.join(source_dir, product_root))
                top_product = rel_to_root.split(os.sep)[0]
                if top_product in skip_products:
                    subdirs[:] = []
                    continue
            subdirs[:] = sorted(d for d in subdirs if d not in skip_dirs)
            if not filenames:
                continue
            rel = os.path.relpath(walk_dir, source_dir)
            tree[rel] = sorted(filenames)
            if dirname == product_root:
                rel_to_root = os.path.relpath(walk_dir, os.path.join(source_dir, product_root))
                top_product = rel_to_root.split(os.sep)[0]
                dir_groups[rel] = product_groups.get(top_product, "CG_" + top_product)
            else:
                # e.g. scripts/, clink/ -> CG_<dirname>
                dir_groups[rel] = "CG_" + dirname
    return tree, dir_groups


def _nest(tree):
    """Flat {rel_dir: [files]} -> nested {_files, children}."""
    root = {}
    for rel_dir, files in sorted(tree.items()):
        if rel_dir == "":
            root["_files"] = files
            continue
        node = root
        for part in rel_dir.replace("/", os.sep).split(os.sep):
            node = node.setdefault("children", {}).setdefault(part, {})
        node["_files"] = files
    return root


def generate_wxs(source_dir, output_path, spec, logger=None):
    """Generate a WiX v4 .wxs (directory tree + per-product ComponentGroups)."""
    tree, dir_groups = _collect_tree(source_dir, spec)
    namespace = spec.get("guid_namespace", "sat-msi")

    output_abs = os.path.abspath(output_path)
    prefix = os.path.relpath(os.path.abspath(source_dir),
                             os.path.dirname(output_abs)).replace("/", "\\")

    nested = _nest(tree)
    group_components = {}
    out = io.StringIO()
    out.write('<?xml version="1.0" encoding="utf-8"?>\n')
    out.write('<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">\n')
    out.write("  <Fragment>\n")
    out.write('    <DirectoryRef Id="INSTALL_ROOT">\n')

    def write_node(node, rel_path, depth):
        ind = "      " + "  " * depth
        if "_files" in node:
            comp_id = "cmp_" + sanitize_id(rel_path)
            guid = _make_guid(namespace, rel_path if rel_path else ".")
            group = dir_groups.get(rel_path, "CG_root")
            group_components.setdefault(group, []).append(comp_id)
            out.write('{}<Component Id="{}" Guid="{}">\n'.format(ind, comp_id, guid))
            for fname in node["_files"]:
                src_rel = (rel_path + os.sep + fname) if rel_path else fname
                src_wix = prefix + "\\" + src_rel.replace(os.sep, "\\")
                out.write('{}  <File Source="{}" />\n'.format(ind, _xml_escape(src_wix)))
            out.write("{}</Component>\n".format(ind))
        for child in sorted(node.get("children", {})):
            child_path = (rel_path + os.sep + child) if rel_path else child
            out.write('{}<Directory Id="dir_{}" Name="{}">\n'.format(
                ind, sanitize_id(child_path), _xml_escape(child)))
            write_node(node["children"][child], child_path, depth + 1)
            out.write("{}</Directory>\n".format(ind))

    write_node(nested, "", 0)
    out.write("    </DirectoryRef>\n  </Fragment>\n\n")

    # Ensure every non-product install_dir has a ComponentGroup, even if the
    # directory is absent at build time (empty group). This lets a Package.wxs
    # feature reference an optional resource (e.g. CG_clink) without breaking the
    # build when that resource was not provided: the feature then installs nothing.
    for d in spec.get("install_dirs", []):
        if d != spec.get("product_root", "W64"):
            group_components.setdefault("CG_" + d, [])

    out.write("  <Fragment>\n")
    for group in sorted(group_components):
        out.write('    <ComponentGroup Id="{}">\n'.format(group))
        for comp_id in group_components[group]:
            out.write('      <ComponentRef Id="{}" />\n'.format(comp_id))
        out.write("    </ComponentGroup>\n")
    out.write("  </Fragment>\n</Wix>\n")

    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out.getvalue())

    n_comp = sum(len(v) for v in group_components.values())
    n_files = sum(len(v) for v in tree.values())
    if logger:
        logger.write("  generated %s\n" % output_path, 4)
        logger.write("  %d components, %d groups, %d files\n"
                     % (n_comp, len(group_components), n_files), 4)
    return n_comp, n_files


# ---------------------------------------------------------------------------
# Staging + wix build orchestration
# ---------------------------------------------------------------------------

def _read_spec(installer_cfg):
    """Extract the tree-walk spec from the ``installer.tree`` config node."""
    tree_cfg = _get(installer_cfg, "tree")
    return {
        "root_install_files": _as_list(_get(tree_cfg, "root_install_files")),
        "install_dirs": _as_list(_get(tree_cfg, "install_dirs")),
        "skip_dirs": _as_list(_get(tree_cfg, "skip_dirs")),
        "skip_products": _as_list(_get(tree_cfg, "skip_products")),
        "product_root": str(_get(tree_cfg, "product_root", "W64")),
        "product_groups": _as_dict(_get(tree_cfg, "product_groups")),
        "guid_namespace": str(_get(installer_cfg, "guid_namespace", "sat-msi")),
    }


def _link_products(src_dir, dst_dir, logger):
    """Reference the products dir (W64) in the staging tree WITHOUT copying it.

    Uses a Windows directory junction (``mklink /J``, instant, no admin needed):
    the multi-GB product tree is referenced in place. Falls back to a full copy
    if the junction cannot be created (e.g. across volumes, or non-Windows).
    """
    # drop any previous link/dir at dst (rmdir removes a junction without
    # touching its target; a real directory is then removed with rmtree).
    if os.path.isdir(dst_dir):
        subprocess.call(["cmd", "/c", "rmdir", dst_dir])
        if os.path.isdir(dst_dir):
            _rmtree_force(dst_dir)
    if src.architecture.is_windows():
        rc = subprocess.call(["cmd", "/c", "mklink", "/J", dst_dir, src_dir],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc == 0:
            return
        logger.write(src.printcolors.printcWarning(
            _("  junction failed, falling back to full copy\n")), 2)
    shutil.copytree(src_dir, dst_dir)


def _stage(config, resources_dir, staging_dir, spec, logger):
    """Assemble a lean staging tree next to the install (hybrid approach).

    The big product tree (W64) is *referenced in place* via a junction — not
    copied. Only the small installer resources and the SAT-generated launcher/
    env files are copied into the staging directory. Project staging fixes then
    run on this tree (patching launcher copies here, and W64 in place through the
    junction — the same benign runtime fixes a hand-written MSI build applies)."""
    install_root = config.APPLICATION.workdir
    product_root = spec["product_root"]

    logger.write("  staging into %s\n" % staging_dir, 3)
    src.ensure_path_exists(staging_dir)

    # 1. copy project installer resources (launchers, scripts, clink, branding, *.wxs).
    #    Remove any existing destination first (clearing read-only attributes) so
    #    re-runs don't fail overwriting read-only files (clink .exe/.dll, etc.).
    for item in sorted(os.listdir(resources_dir)):
        s = os.path.join(resources_dir, item)
        d = os.path.join(staging_dir, item)
        if os.path.isdir(s):
            _rmtree_force(d)
            shutil.copytree(s, d)
        else:
            _remove_file_force(d)
            shutil.copy2(s, d)

    # 2. copy the small SAT-generated launcher / env root files (salome, env_launch.bat…)
    #    so they are patched in the staging copy, leaving the real install untouched.
    for fname in spec["root_install_files"]:
        s = os.path.join(install_root, fname)
        if os.path.isfile(s):
            d = os.path.join(staging_dir, fname)
            _remove_file_force(d)
            shutil.copy2(s, d)

    # 3. reference the products dir (W64) in place — junction, no multi-GB copy.
    src_products = os.path.join(install_root, product_root)
    if not os.path.isdir(src_products):
        raise src.SatException(
            _("products directory not found: %s (run 'sat compile' first)") % src_products)
    _link_products(src_products, os.path.join(staging_dir, product_root), logger)


def _run_pre_build(installer_cfg, staging_dir, config, logger):
    """Run the optional project staging script (SALOME runtime fixes)."""
    script = _get(installer_cfg, "pre_build_script")
    if not script:
        return
    script_path = os.path.join(staging_dir, script)
    if not os.path.isfile(script_path):
        logger.write(src.printcolors.printcWarning(
            _("  pre_build script not found: %s\n") % script_path), 2)
        return
    python_exe = os.path.join(staging_dir,
                              _get(installer_cfg, "python_in_tree", "W64/Python/python.exe"))
    interp = python_exe if os.path.isfile(python_exe) else "python"
    logger.write("  running pre_build script %s\n" % script, 3)
    rc = subprocess.call([interp, script_path], cwd=staging_dir)
    if rc != 0:
        raise src.SatException(_("pre_build script failed (code %d)") % rc)


def build_msi(config, options, logger):
    """Build the Windows MSI for the given application.

    Returns a src.returnCode-style int (0 = OK).
    Requires an ``APPLICATION.installer`` section (provided by the project).
    """
    if not src.architecture.is_windows():
        logger.write(src.printcolors.printcError(
            _("--build_msi is only supported on Windows.\n")), 1)
        return 1

    src.check_config_has_application(config)

    installer_cfg = _find_installer_cfg(config)
    if installer_cfg is None:
        logger.write(src.printcolors.printcError(_(
            "No 'installer' section found in the application or project config.\n"
            "The project must define an 'installer' section (resources_dir, "
            "wxs_sources, tree, ...). For SALOME see sat_salome/installer/windows.\n")), 1)
        return 1

    # --- resolve config ---
    resources_dir = _get(installer_cfg, "resources_dir")
    if not resources_dir or not os.path.isdir(resources_dir):
        logger.write(src.printcolors.printcError(
            _("installer.resources_dir not found: %s\n") % resources_dir), 1)
        return 1

    wxs_sources = _as_list(_get(installer_cfg, "wxs_sources"))
    generated_wxs = str(_get(installer_cfg, "generated_wxs", "w64_files.wxs"))
    wix_arch = str(_get(installer_cfg, "wix_arch", "x64"))
    wix_exts = _as_list(_get(installer_cfg, "wix_extensions"))
    spec = _read_spec(installer_cfg)

    # output name (APPLICATION.name already carries the version, e.g. SALOME-9.16.0)
    default_out = "%s-win64.msi" % config.APPLICATION.name
    output_name = str(_get(installer_cfg, "output_name", default_out))
    if getattr(options, "name", None):
        output_name = options.name if options.name.endswith(".msi") else options.name + ".msi"

    staging_dir = str(_get(installer_cfg, "staging_dir",
                           os.path.join(config.APPLICATION.workdir, "MSI")))
    build_dir = os.path.join(staging_dir, "build")
    output_path = os.path.join(build_dir, output_name)

    logger.write(src.printcolors.printcHeader(
        _("\nBuilding MSI installer for %s\n") % config.APPLICATION.name), 1)

    # --- check wix ---
    if shutil.which("wix") is None:
        logger.write(src.printcolors.printcError(_(
            "'wix' not found in PATH. Install WiX Toolset v4: "
            "dotnet tool install --global wix\n")), 1)
        return 1

    try:
        # 1. stage
        _stage(config, resources_dir, staging_dir, spec, logger)
        # 2. project staging fixes (optional)
        _run_pre_build(installer_cfg, staging_dir, config, logger)
        # 3. generate w64_files.wxs
        logger.write("  generating WiX source ...\n", 2)
        generate_wxs(staging_dir, os.path.join(staging_dir, generated_wxs), spec, logger)
        # 4. wix build
        src.ensure_path_exists(build_dir)
        cmd = ["wix", "build", "-arch", wix_arch, "-o", output_path]
        for ext in wix_exts:
            cmd += ["-ext", ext]
        cmd += list(wxs_sources) + [generated_wxs]
        logger.write("  %s\n" % " ".join(cmd), 3)
        rc = subprocess.call(cmd, cwd=staging_dir)
        if rc != 0:
            logger.write(src.printcolors.printcError(
                _("\nwix build failed (code %d)\n") % rc), 1)
            return 1
    except src.SatException as e:
        logger.write(src.printcolors.printcError("\n%s\n" % str(e)), 1)
        return 1

    logger.write(src.printcolors.printcSuccess(
        _("\nMSI created: %s\n") % output_path), 1)
    return 0
