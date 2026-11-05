#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2026  CEA, EDF
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
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA


"""
Builder of the dmg archive of the package command (sat package --archive dmg):
produces a macOS application bundle (NAME.app) and a disk image (.dmg).

The content of the bundle is the content of the archive that the package
command would have put in the tar file (binaries, launcher, and optionally
sources, project, salomeTools, additional files). It is copied into
NAME.app/Contents/Resources/, then made relocatable on any Mac:

  - absolute dependencies outside the system are rewritten to @rpath/...,
    libraries that are not part of the application (gcc runtime: libgfortran,
    libquadmath, libgcc_s...) are embedded in BINARIES-<dist>/_external/lib
  - absolute LC_RPATHs (the build directory) are removed and replaced by
    @loader_path relative rpaths
  - absolute shebangs are replaced by #!/usr/bin/env <interpreter>
  - Contents/MacOS/NAME runs the relative sat launcher with the embedded Python

The bundle can also be built from an archive produced by "sat package -b".
"""

import os
import re
import sys
import glob
import shutil
import struct
import stat
import tarfile
import platform
import plistlib
import subprocess

import src
import src.debug as DBG

DEFAULT_NAME = "SALOME"
DEFAULT_BUNDLE_ID = "org.salome-platform.salome"
REQUIRED_TOOLS = ("otool", "install_name_tool", "codesign", "hdiutil",
                  "sips", "iconutil", "xattr")

IGNORED_DIRS = set([".git", ".svn"])

# --------------------------------------------------------------------------
# Mach-O
# --------------------------------------------------------------------------
MH_MAGIC = 0xfeedface
MH_MAGIC_64 = 0xfeedfacf
FAT_MAGIC = 0xcafebabe
FAT_MAGIC_64 = 0xcafebabf
MH_EXECUTE, MH_DYLIB, MH_BUNDLE = 2, 6, 8
LINKABLE_FILETYPES = (MH_EXECUTE, MH_DYLIB, MH_BUNDLE)

LOAD_DYLIB_CMDS = ("LC_LOAD_DYLIB", "LC_LOAD_WEAK_DYLIB", "LC_REEXPORT_DYLIB",
                   "LC_LAZY_LOAD_DYLIB", "LC_LOAD_UPWARD_DYLIB")
SYSTEM_PREFIXES = ("/usr/lib/", "/System/")
LIB_EXTENSIONS = (".dylib", ".so")


def macho_filetype(path):
    '''Returns the Mach-O file type (MH_EXECUTE, MH_DYLIB...) of path,
       None if it is not a Mach-O file. For universal files, the type of
       the first architecture is returned.'''
    try:
        with open(path, "rb") as f:
            head = f.read(32)
            if len(head) < 16:
                return None
            magic = struct.unpack("<I", head[:4])[0]
            if magic in (MH_MAGIC, MH_MAGIC_64):
                return struct.unpack("<I", head[12:16])[0]
            magic = struct.unpack(">I", head[:4])[0]
            if magic not in (FAT_MAGIC, FAT_MAGIC_64):
                return None
            nfat = struct.unpack(">I", head[4:8])[0]
            if not 0 < nfat < 32:          # Java class files share FAT_MAGIC
                return None
            if magic == FAT_MAGIC:         # fat_arch: cputype, subtype, offset...
                offset = struct.unpack(">I", head[16:20])[0]
            else:                          # fat_arch_64: offset is 64 bits
                offset = struct.unpack(">Q", head[16:24])[0]
            f.seek(offset)
            sub = f.read(16)
            if len(sub) < 16:
                return None
            if struct.unpack("<I", sub[:4])[0] not in (MH_MAGIC, MH_MAGIC_64):
                return None
            return struct.unpack("<I", sub[12:16])[0]
    except (IOError, OSError, struct.error):
        return None


def is_linkable_macho(path):
    return macho_filetype(path) in LINKABLE_FILETYPES


def _run(cmd, **kwargs):
    '''subprocess.run with text output'''
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    return subprocess.run(cmd, universal_newlines=True, **kwargs)


class MachOInfo(object):
    '''Load commands of a Mach-O file (first architecture), read with otool -l'''

    def __init__(self, path):
        self.path = path
        self.id = None
        self.deps = []
        self.rpaths = []     # in file order, duplicates kept
        self.minos = None
        res = _run(["otool", "-l", path])
        arch_sections = 0
        cmd = None
        for line in res.stdout.splitlines():
            if "(architecture " in line and line.rstrip().endswith(":"):
                arch_sections += 1
                if arch_sections > 1:
                    break                  # only the first architecture
                continue
            s = line.strip()
            if s.startswith("cmd "):
                cmd = s.split()[1]
                continue
            if cmd in LOAD_DYLIB_CMDS and s.startswith("name "):
                dep = s[5:].rsplit(" (offset", 1)[0].strip()
                if dep not in self.deps:
                    self.deps.append(dep)
            elif cmd == "LC_ID_DYLIB" and s.startswith("name "):
                self.id = s[5:].rsplit(" (offset", 1)[0].strip()
            elif cmd == "LC_RPATH" and s.startswith("path "):
                self.rpaths.append(s[5:].rsplit(" (offset", 1)[0].strip())
            elif cmd == "LC_BUILD_VERSION" and s.startswith("minos "):
                self.minos = s.split()[1]
            elif cmd == "LC_VERSION_MIN_MACOSX" and s.startswith("version "):
                self.minos = s.split()[1]

    def dependencies(self):
        '''dependencies without the id of the library itself'''
        return [d for d in self.deps if d != self.id]


def loader_rpath(file_path, target_dir):
    '''@loader_path relative rpath from file_path to target_dir'''
    rel = os.path.relpath(os.path.realpath(target_dir),
                          os.path.realpath(os.path.dirname(file_path)))
    return "@loader_path" if rel == "." else "@loader_path/" + rel


# --------------------------------------------------------------------------
# Relocation of the Mach-O files of the bundle
# --------------------------------------------------------------------------
class BundleRelocator(object):

    def __init__(self, logger, resources_dir, binaries_dir, keep_abs_rpaths=False):
        self.logger = logger
        self.resources_dir = resources_dir
        self.binaries_dir = binaries_dir
        self.ext_dir = os.path.join(binaries_dir, "_external", "lib")
        self.keep_abs_rpaths = keep_abs_rpaths
        self.index = {}        # library name -> real directory
        self.queue = []
        self.nb_modified = 0
        self.embedded = []
        self.origin = {}       # embedded library -> its original path
        self.warnings = []

    def short(self, path):
        return os.path.relpath(path, self.resources_dir)

    def warn(self, msg):
        self.warnings.append(msg)
        self.logger.write("  %s %s\n" % (src.printcolors.printcWarning("WARNING:"), msg), 1)

    # -- inventory ---------------------------------------------------------
    def build_index(self):
        '''name -> directory of every library of the bundle. Symbolic links are
           indexed too: dependencies often point to libfoo.1.dylib which is a
           link to libfoo.1.2.3.dylib'''
        for root, dirs, files in os.walk(self.binaries_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            real_root = os.path.realpath(root)
            for name in files + dirs:
                if name.endswith(LIB_EXTENSIONS):
                    self.index.setdefault(name, real_root)

    def scan(self):
        for root, dirs, files in os.walk(self.resources_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for name in files:
                path = os.path.join(root, name)
                if not os.path.islink(path) and is_linkable_macho(path):
                    self.queue.append(path)
        return len(self.queue)

    def find_rpath_dir(self, name):
        '''directory D of the bundle such that D/name exists
           (name = libfoo.dylib or QtCore.framework/Versions/A/QtCore)'''
        if "/" not in name:
            return self.index.get(name)
        candidates = glob.glob(os.path.join(self.binaries_dir, "*", "lib", name))
        candidates += glob.glob(os.path.join(self.ext_dir, name))
        if candidates:
            return os.path.realpath(candidates[0][:-len(name) - 1])
        return None

    # -- external libraries ---------------------------------------------------
    def embed_external(self, src_path):
        '''copies a library that is not part of the application into
           _external/lib; it is added to the queue to be relocated too'''
        name = os.path.basename(src_path)
        src.ensure_path_exists(self.ext_dir)
        dst = os.path.join(self.ext_dir, name)
        if not os.path.exists(dst):
            shutil.copy2(os.path.realpath(src_path), dst)
            os.chmod(dst, os.stat(dst).st_mode | stat.S_IWUSR)
            _run(["install_name_tool", "-id", "@rpath/" + name, dst])
            self.queue.append(dst)
            self.origin[dst] = os.path.realpath(src_path)
            self.embedded.append(src_path)
            self.logger.write("  embedded: %s\n" % src_path, 3)
        self.index[name] = os.path.realpath(self.ext_dir)
        return self.index[name]

    def embed_rpath_dependency(self, path, name, search_dirs):
        '''@rpath/name dependency of path, not in the bundle: looks for it in
           search_dirs (original rpaths) and embeds it. Returns the directory
           of the bundle that contains it, None if not found.'''
        resources_real = os.path.realpath(self.resources_dir) + os.sep
        for d in search_dirs:
            candidate = os.path.join(d, name)
            if not os.path.isfile(candidate):
                continue
            if os.path.realpath(candidate).startswith(resources_real):
                continue
            if "/" in name:
                self.warn("%s: external framework %s (found in %s) not handled "
                          "(embed it by hand)" % (self.short(path), name, d))
                return None
            return self.embed_external(candidate)
        return None

    # -- relocation of one file ------------------------------------------------
    def relocate(self, path):
        info = MachOInfo(path)
        fdir = os.path.dirname(path)
        args = []
        wanted = []

        # existing rpaths: @... kept, absolute ones removed (build directory)
        kept = []
        seen = set()
        for rp in info.rpaths:
            if rp in seen:
                continue
            seen.add(rp)
            if rp.startswith("@") or self.keep_abs_rpaths:
                kept.append(rp)
            else:
                args += ["-delete_rpath", rp]
        kept_dirs = []
        for rp in kept:
            if rp.startswith("@loader_path"):
                kept_dirs.append(fdir + rp[len("@loader_path"):])
            elif not rp.startswith("@"):
                kept_dirs.append(rp)

        # directories where the dependencies were found before the copy:
        # all the original rpaths, @loader_path being the ORIGINAL location
        # of the file for an embedded library (e.g. Homebrew gcc: libgfortran
        # loads @rpath/libgcc_s.1.1.dylib next to it)
        orig_dir = os.path.dirname(self.origin.get(path, path))
        orig_dirs = []
        for rp in info.rpaths:
            if rp.startswith("@loader_path"):
                orig_dirs.append(orig_dir + rp[len("@loader_path"):])
            elif not rp.startswith("@"):
                orig_dirs.append(rp)

        def want(target_dir):
            rp = loader_rpath(path, target_dir)
            if rp not in wanted:
                wanted.append(rp)

        for dep in info.dependencies():
            if dep.startswith("@rpath/"):
                # still resolved once the absolute rpaths are removed?
                name = dep[len("@rpath/"):]
                if any(os.path.exists(os.path.join(d, name)) for d in kept_dirs):
                    continue
                target = self.find_rpath_dir(name)
                if target is None:
                    # found outside of the bundle through the original rpaths:
                    # library that does not belong to the application -> embedded
                    target = self.embed_rpath_dependency(path, name, orig_dirs)
                if target:
                    want(target)
                continue           # unresolved: reported by verify()
            if dep.startswith("@") or dep.startswith(SYSTEM_PREFIXES):
                continue
            if ".framework/" in dep:
                self.warn("%s: external framework %s not handled (embed it by hand)"
                          % (self.short(path), dep))
                continue
            name = os.path.basename(dep)
            target = self.index.get(name)
            if target is None:
                if os.path.isfile(dep):
                    target = self.embed_external(dep)
                else:
                    self.warn("%s: dependency %s missing on this machine"
                              % (self.short(path), dep))
                    continue
            args += ["-change", dep, "@rpath/" + name]
            want(target)

        for rp in wanted:
            if rp not in kept:
                args += ["-add_rpath", rp]

        if not args:
            return
        res = _run(["install_name_tool"] + args + [path])
        if res.returncode != 0:
            err = [l for l in res.stderr.splitlines()
                   if "invalidate the code signature" not in l]
            if any("do not fit" in l for l in err):
                self.warn("%s: not enough header space, link it with "
                          "-Wl,-headerpad_max_install_names" % self.short(path))
            else:
                self.warn("%s: install_name_tool failed: %s"
                          % (self.short(path), err[0] if err else res.returncode))
            return
        self.nb_modified += 1

    def relocate_all(self):
        i = 0
        while i < len(self.queue):     # the queue grows with embedded libraries
            self.relocate(self.queue[i])
            i += 1
            if i % 1000 == 0:
                self.logger.write("  %d / %d\n" % (i, len(self.queue)), 3)

    # -- verification ------------------------------------------------------
    def verify(self):
        problems = []
        for path in self.queue:
            info = MachOInfo(path)
            fdir = os.path.dirname(path)
            dirs = []
            exe_relative = False
            for rp in info.rpaths:
                if rp.startswith("@loader_path"):
                    dirs.append(fdir + rp[len("@loader_path"):])
                elif rp.startswith("@executable_path"):
                    exe_relative = True     # depends on the process: not checked
                else:
                    dirs.append(rp)
            dups = sorted(set(rp for rp in info.rpaths if info.rpaths.count(rp) > 1))
            if dups:
                problems.append("%s: duplicate LC_RPATH %s (rejected by recent dyld)"
                                % (self.short(path), ", ".join(dups)))
            for dep in info.dependencies():
                if dep.startswith(SYSTEM_PREFIXES) or dep.startswith("@executable_path/"):
                    continue
                if dep.startswith("@rpath/"):
                    name = dep[len("@rpath/"):]
                    if exe_relative or any(os.path.exists(os.path.join(d, name)) for d in dirs):
                        continue
                    problems.append("%s: %s unresolved" % (self.short(path), dep))
                elif dep.startswith("@loader_path/"):
                    if not os.path.exists(os.path.join(fdir, dep[len("@loader_path/"):])):
                        problems.append("%s: %s missing" % (self.short(path), dep))
                else:
                    problems.append("%s: absolute dependency %s" % (self.short(path), dep))
        return problems

    # -- signatures ----------------------------------------------------------
    def fix_signatures(self):
        '''ad hoc re-signature of the files whose (linker) signature is invalid'''
        nb = 0
        for path in self.queue:
            if _run(["codesign", "-v", path]).returncode != 0:
                res = _run(["codesign", "-f", "-s", "-", path])
                if res.returncode != 0:
                    self.warn("%s: codesign failed" % self.short(path))
                nb += 1
        return nb

    def minos(self, path):
        return MachOInfo(path).minos



def _copy_tree(src_dir, dst_dir):
    '''copies src_dir into dst_dir (merged if it exists), symbolic links kept,
       VCS directories ignored, files made writable by the user'''
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        rel = os.path.relpath(root, src_dir)
        target_dir = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        src.ensure_path_exists(target_dir)
        for name in list(dirs) + files:
            s = os.path.join(root, name)
            t = os.path.join(target_dir, name)
            if os.path.islink(s):
                if os.path.lexists(t):
                    os.remove(t)
                os.symlink(os.readlink(s), t)
                if name in dirs:
                    dirs.remove(name)      # do not descend into a linked directory
            elif name in files:
                if os.path.lexists(t):
                    os.remove(t)
                shutil.copy2(s, t)
                os.chmod(t, os.stat(t).st_mode | stat.S_IWUSR)




def populate_from_files(logger, d_files, resources_dir):
    '''copies the content of the archive (dictionary built by the package
       command: label -> (path_on_local_machine, path_in_archive)) into
       resources_dir. Returns (path of the logs archive, [(source, destination)])'''
    d_files = dict(d_files)
    logs = d_files.pop("LOGS", (None, None))[0]

    copied = set()
    mapping = []
    max_len = max(len(k) for k in d_files) if d_files else 0
    for label in sorted(d_files):
        local_path, path_in_bundle = d_files[label]
        if (local_path, path_in_bundle) in copied:
            continue
        copied.add((local_path, path_in_bundle))
        if not os.path.exists(local_path):
            logger.write("  %s %s not found\n"
                         % (src.printcolors.printcWarning("WARNING:"), local_path), 1)
            continue
        dest = os.path.join(resources_dir, path_in_bundle)
        logger.write("  %s %s %s\n" % (label, "." * (max_len - len(label) + 3),
                                       path_in_bundle), 3)
        if os.path.isdir(local_path):
            _copy_tree(local_path, dest)
            mapping.append((local_path, dest))
            if os.path.realpath(local_path) != local_path:
                mapping.append((os.path.realpath(local_path), dest))
        else:
            src.ensure_path_exists(os.path.dirname(dest))
            shutil.copy2(local_path, dest)
    return logs, mapping

def populate_from_archive(logger, archive, resources_dir, tmp_dir, launcher_name):
    '''extracts an archive made by "sat package -b" into resources_dir'''
    logger.write("  extracting %s\n" % archive, 3)
    extract_dir = os.path.join(tmp_dir, "extract")
    src.ensure_path_exists(extract_dir)
    with tarfile.open(archive) as tar:
        if hasattr(tarfile, "tar_filter"):
            tar.extractall(extract_dir, filter="tar")
        else:
            tar.extractall(extract_dir)
    top = None
    for name in sorted(os.listdir(extract_dir)):
        cand = os.path.join(extract_dir, name)
        if os.path.isfile(os.path.join(cand, launcher_name)):
            top = cand
            break
    if top is None:
        raise src.SatException(_("no '%s' launcher at the root of the archive %s "
                                 "(archive made with 'sat package -b'?)")
                               % (launcher_name, archive))
    shutil.move(top, resources_dir)
    logs = os.path.join(resources_dir, "logs.tgz")
    return (logs if os.path.isfile(logs) else None), []


def fix_absolute_symlinks(logger, resources_dir, mapping):
    '''absolute symbolic links pointing into a copied directory -> relative
       links (a link pointing outside of the bundle breaks it on another Mac
       and prevents the signature of the bundle)'''
    nb_fixed = 0
    outside = []
    for root, dirs, files in os.walk(resources_dir):
        for name in dirs + files:
            path = os.path.join(root, name)
            if not os.path.islink(path):
                continue
            target = os.readlink(path)
            if not os.path.isabs(target):
                continue
            new_target = None
            for src_dir, dest_dir in mapping:
                if target == src_dir or target.startswith(src_dir + os.sep):
                    new_target = dest_dir + target[len(src_dir):]
                    break
            if new_target is None:
                outside.append((path, target))
                continue
            os.remove(path)
            os.symlink(os.path.relpath(new_target, root), path)
            nb_fixed += 1
    for path, target in outside:
        logger.write("  %s %s -> %s (outside of the bundle)\n"
                     % (src.printcolors.printcWarning("WARNING:"),
                        os.path.relpath(path, resources_dir), target), 1)
    return nb_fixed


def slim(binaries_dir):
    '''removes the development files'''
    for prod in os.listdir(binaries_dir):
        inc = os.path.join(binaries_dir, prod, "include")
        if os.path.isdir(inc) and not os.path.islink(inc):
            shutil.rmtree(inc)
    for root, dirs, files in os.walk(binaries_dir, topdown=True):
        for d in list(dirs):
            if os.path.basename(root) == "lib" and d in ("pkgconfig", "cmake"):
                shutil.rmtree(os.path.join(root, d))
                dirs.remove(d)
        for f in files:
            if f.endswith((".a", ".la")):
                os.remove(os.path.join(root, f))


SHEBANG_SYSTEM_DIRS = ("/bin/", "/usr/bin/", "/sbin/", "/usr/sbin/")


def fix_shebangs(resources_dir):
    '''#!/build/INSTALL/Python/bin/python3 -> #!/usr/bin/env python3
       (the sat launcher puts the bin/ directories of the bundle in PATH)'''
    nb = 0
    for root, dirs, files in os.walk(resources_dir):
        for name in files:
            path = os.path.join(root, name)
            if os.path.islink(path) or not os.access(path, os.X_OK):
                continue
            try:
                with open(path, "rb") as f:
                    if f.read(2) != b"#!":
                        continue
                    f.seek(0)
                    content = f.read()
            except (IOError, OSError):
                continue
            eol = content.find(b"\n")
            first = content[2:eol if eol >= 0 else len(content)].strip()
            if not first:
                continue
            prog, _sep, rest = first.partition(b" ")
            prog_s = prog.decode("utf-8", "replace")
            if prog_s.startswith(SHEBANG_SYSTEM_DIRS) or not prog_s.startswith("/"):
                continue
            new_first = b"#!/usr/bin/env " + os.path.basename(prog)
            if rest:
                new_first += b" " + rest
            body = content[eol:] if eol >= 0 else b"\n"
            with open(path, "wb") as f:       # same inode: permissions kept
                f.write(new_first + body)
            nb += 1
    return nb


STUB_TEMPLATE = r'''#!/bin/bash
# Launcher of the bundle @NAME@.app, generated by "sat package --archive dmg".
# Runs the relative sat launcher Contents/Resources/@LAUNCHER@ with the
# embedded Python. Command line use is supported, through a symbolic link too:
#   ln -s /Applications/@NAME@.app/Contents/MacOS/@NAME@ /usr/local/bin/@LAUNCHER@
src="$0"
while [ -L "$src" ]; do
    t=$(readlink "$src")
    case "$t" in /*) src=$t ;; *) src=$(dirname "$src")/$t ;; esac
done
RES="$(cd "$(dirname "$src")/../Resources" && pwd -P)"

export PYTHONDONTWRITEBYTECODE=1
export LANG="${LANG:-en_US.UTF-8}"
# Dock icon of the SALOME GUI (macOS Dock icon patch of the GUI module)
[ -f "$RES/@NAME@.png" ] && export SALOME_APP_ICON="$RES/@NAME@.png"

args=()
for a in "$@"; do
    case "$a" in -psn_*) ;; *) args+=("$a") ;; esac   # added by the Finder (old macOS)
done

# launched from the Finder (no terminal): output to a log file
if [ -z "${TERM:-}" ]; then
    mkdir -p "$HOME/Library/Logs/@NAME@"
    exec >>"$HOME/Library/Logs/@NAME@/@NAME@.log" 2>&1
    echo "=== $(date) ==="
fi

exec "$RES/@PYTHON@" "$RES/@LAUNCHER@" "${args[@]}"
'''


def write_stub(path, name, launcher_name, python_rel):
    content = (STUB_TEMPLATE.replace("@NAME@", name)
                            .replace("@LAUNCHER@", launcher_name)
                            .replace("@PYTHON@", python_rel))
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o755)


def write_info_plist(path, name, bundle_id, version, minos, icon_file):
    plist = {
        "CFBundleName": name,
        "CFBundleDisplayName": name,
        "CFBundleIdentifier": bundle_id,
        "CFBundleVersion": version,
        "CFBundleShortVersionString": version,
        "CFBundleExecutable": name,
        "CFBundlePackageType": "APPL",
        "CFBundleInfoDictionaryVersion": "6.0",
        "LSMinimumSystemVersion": minos,
        "NSHighResolutionCapable": True,
    }
    if icon_file:
        plist["CFBundleIconFile"] = icon_file
    with open(path, "wb") as f:
        plistlib.dump(plist, f)


def make_icon(icon, resources_dir, name, tmp_dir):
    '''copies or builds (from a png) NAME.icns, and NAME.png used by the GUI
       for its Dock icon; returns the file name of the .icns'''
    icns = os.path.join(resources_dir, name + ".icns")
    png = os.path.join(resources_dir, name + ".png")   # Dock icon of the GUI
    if icon.endswith(".icns"):
        shutil.copy2(icon, icns)
        _run(["sips", "-s", "format", "png", icns, "--out", png])
        return os.path.basename(icns)
    if not icon.endswith(".png"):
        raise src.SatException(_("icon: .icns or .png file expected (%s)") % icon)
    shutil.copy2(icon, png)
    iconset = os.path.join(tmp_dir, name + ".iconset")
    src.ensure_path_exists(iconset)
    for size in (16, 32, 128, 256, 512):
        for scale, suffix in ((1, ""), (2, "@2x")):
            px = str(size * scale)
            _run(["sips", "-z", px, px, icon, "--out",
                  os.path.join(iconset, "icon_%dx%d%s.png" % (size, size, suffix))])
    res = _run(["iconutil", "-c", "icns", iconset, "-o", icns])
    if res.returncode != 0:
        raise src.SatException(_("iconutil failed: %s") % res.stderr)
    return os.path.basename(icns)




# --------------------------------------------------------------------------
# Entry points (called by commands/package.py)
# --------------------------------------------------------------------------
def _step(logger, msg):
    logger.write("\n%s\n" % src.printcolors.printcLabel(msg), 2)


def _error(logger, msg):
    logger.write(src.printcolors.printcError(msg) + "\n", 1)


def check_prerequisites(logger):
    '''the dmg archive is only available on macOS, with the Xcode Command
       Line Tools. Returns True if the bundle can be built'''
    if platform.system() != "Darwin":
        _error(logger, _("Error: the dmg archive is only available on macOS"))
        return False
    for tool in REQUIRED_TOOLS:
        if shutil.which(tool) is None:
            _error(logger, _("Error: %s not found (Xcode Command Line Tools?)") % tool)
            return False
    return True


def get_bundle_version(config, options, from_archive=None):
    '''--bundle_version, else the SALOME version, else a version found in the
       name of the archive, else 1.0'''
    version = options.bundle_version
    if not version and "APPLICATION" in config:
        try:
            version = str(src.get_salome_version(config))
        except Exception:
            version = ""
    if not version and from_archive:
        m = re.search(r"\d+\.\d+(\.\d+)?", os.path.basename(from_archive))
        version = m.group(0) if m else ""
    return version or "1.0"


def build_dmg(config, logger, options, outdir, name, d_files=None, from_archive=None):
    '''builds outdir/name.app and outdir/name-<version>-<dist>-<arch>.dmg

    :param config Config: The global configuration.
    :param logger Logger: the logging instance
    :param options OptResult: the options of the package command
    :param outdir str: the output directory
    :param name str: the name of the bundle
    :param d_files dict: the content of the archive, built by the package
                         command: label -> (path_on_local_machine, path_in_archive)
    :param from_archive str: an archive made by "sat package -b", used
                             instead of d_files
    :return: 0 if OK, 1 if the bundle could not be built or has problems
    :rtype: int
    '''
    launcher_name = src.get_launcher_name(config) if "APPLICATION" in config else "salome"
    version = get_bundle_version(config, options, from_archive)

    src.ensure_path_exists(outdir)
    outdir = os.path.realpath(outdir)
    app_final = os.path.join(outdir, name + ".app")
    dmg = os.path.join(outdir, "%s-%s-%s-%s.dmg"
                       % (name, version, config.VARS.dist, platform.machine()))
    for p in ([app_final] + ([] if options.no_dmg else [dmg])):
        if os.path.lexists(p):
            if not options.replace:
                _error(logger, _("Error: %s already exists (use --replace)") % p)
                return 1
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)

    if options.icon and not os.path.isfile(options.icon):
        _error(logger, _("Error: icon %s not found") % options.icon)
        return 1

    src.printcolors.print_value(logger, "Bundle", app_final, 2)
    if not options.no_dmg:
        src.printcolors.print_value(logger, "Disk image", dmg, 2)

    # working directory on the same filesystem as the output: the bundle
    # (several GB) is moved, not copied
    tmp_dir = os.path.join(outdir, ".package_dmg_" + config.VARS.datehour)
    stage_dir = os.path.join(tmp_dir, "dmg")
    app = os.path.join(stage_dir, name + ".app")
    contents = os.path.join(app, "Contents")
    resources_dir = os.path.join(contents, "Resources")
    src.ensure_path_exists(os.path.join(contents, "MacOS"))

    try:
        _step(logger, _("Preparation of the content of the bundle"))
        if from_archive:
            logs, mapping = populate_from_archive(logger, os.path.abspath(from_archive),
                                                  resources_dir, tmp_dir, launcher_name)
        else:
            src.ensure_path_exists(resources_dir)
            logs, mapping = populate_from_files(logger, d_files or {}, resources_dir)
        return _build(config, logger, options, name, version, launcher_name,
                      logs, mapping, tmp_dir, stage_dir, app, app_final, dmg,
                      resources_dir, outdir)
    except src.SatException as e:
        _error(logger, "\n%s" % str(e))
        return 1
    except KeyboardInterrupt:
        _error(logger, "\nERROR: forced interruption")
        return 1
    finally:
        if os.path.isdir(tmp_dir) and not DBG.isDeveloper():
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _build(cfg, logger, options, name, version, launcher_name, logs, mapping,
           tmp_dir, stage_dir, app, app_final, dmg, resources_dir, outdir):
    contents = os.path.dirname(resources_dir)

    if logs and os.path.isfile(logs):
        logs_dest = os.path.join(outdir, "%s-%s-build-logs.tgz" % (name, version))
        shutil.move(logs, logs_dest)
        logger.write("  build logs: %s\n" % logs_dest, 3)

    binaries = sorted(glob.glob(os.path.join(resources_dir, "BINARIES-*")))
    if not binaries:
        raise src.SatException(_("no BINARIES-* directory in the bundle"))
    binaries_dir = binaries[0]
    pythons = sorted(glob.glob(os.path.join(binaries_dir, "*", "bin", "python3")))
    if not pythons:
        raise src.SatException(_("embedded Python not found (BINARIES-*/*/bin/python3)"))
    python_abs = pythons[0]
    python_rel = os.path.relpath(python_abs, resources_dir)
    logger.write("  python: %s\n" % python_rel, 3)
    if not os.path.isfile(os.path.join(resources_dir, launcher_name)):
        raise src.SatException(_("launcher %s not found in the bundle") % launcher_name)

    nb = fix_absolute_symlinks(logger, resources_dir, mapping)
    logger.write("  %d absolute symbolic links made relative\n" % nb, 3)

    if options.slim:
        _step(logger, _("Removal of the development files"))
        slim(binaries_dir)

    # 2. Mach-O relocation --------------------------------------------------------
    _step(logger, _("Relocation of the binaries"))
    relocator = BundleRelocator(logger, resources_dir, binaries_dir)
    relocator.build_index()
    nb = relocator.scan()
    logger.write("  %d Mach-O files\n" % nb, 2)
    relocator.relocate_all()
    logger.write("  %d files modified, %d external libraries embedded\n"
                 % (relocator.nb_modified, len(relocator.embedded)), 2)
    for lib in relocator.embedded:
        logger.write("    + %s\n" % lib, 2)

    _step(logger, _("Verification of the dependencies"))
    problems = relocator.verify()
    for p in problems:
        logger.write("  %s %s\n" % (src.printcolors.printcWarning("WARNING:"), p), 1)
    if problems:
        logger.write("  %s\n" % src.printcolors.printcWarning(
            _("%d problems: the bundle may not work on another Mac") % len(problems)), 1)
    else:
        logger.write("  %s\n" % src.printcolors.printcSuccess(
            _("all dependencies resolve inside the bundle")), 2)

    _step(logger, _("Shebangs"))
    nb = fix_shebangs(resources_dir)
    logger.write("  %d scripts fixed\n" % nb, 2)

    # 3. bundle structure ------------------------------------------------------
    _step(logger, _("Bundle structure"))
    write_stub(os.path.join(contents, "MacOS", name), name, launcher_name, python_rel)
    icon_file = make_icon(os.path.abspath(options.icon), resources_dir, name, tmp_dir) \
                if options.icon else None
    minos = relocator.minos(python_abs) or "11.0"
    bundle_id = options.bundle_id or DEFAULT_BUNDLE_ID
    write_info_plist(os.path.join(contents, "Info.plist"), name, bundle_id,
                     version, minos, icon_file)
    logger.write("  Info.plist: %s %s, macOS >= %s\n" % (bundle_id, version, minos), 2)

    _step(logger, _("Precompilation of the Python modules"))
    # embedded Python, to get the right magic number. Failures (Python 2
    # files, templates...) are expected and ignored
    _run([python_abs, "-m", "compileall", "-q", "-j", "0", resources_dir])

    if not options.no_test:
        _step(logger, _("Launch test"))
        code = "import salome; print('PACKAGE_DMG_OK')"
        env = {"HOME": os.environ.get("HOME", "/tmp"), "TERM": "dumb",
               "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}
        res = _run([os.path.join(contents, "MacOS", name), "shell", "--",
                    "python3", "-c", code], env=env, stderr=subprocess.STDOUT)
        if "PACKAGE_DMG_OK" in res.stdout:
            logger.write("  %s\n" % src.printcolors.printcSuccess("import salome: OK"), 2)
        else:
            logger.write("  %s\n%s\n" % (src.printcolors.printcWarning(
                _("WARNING: launch test failed")), "\n".join(res.stdout.splitlines()[-20:])), 1)

    # 4. signatures --------------------------------------------------------------
    _step(logger, _("Signatures"))
    nb = relocator.fix_signatures()
    logger.write("  %d invalid signatures fixed (ad hoc)\n" % nb, 2)
    _run(["xattr", "-cr", app])
    if options.sign_adhoc:
        res = _run(["codesign", "-f", "-s", "-", app])
        if res.returncode == 0:
            res = _run(["codesign", "-vv", "--strict", app])
        if res.returncode != 0:
            raise src.SatException(_("signature of the bundle failed:\n%s") % res.stderr)
        logger.write("  bundle signed (ad hoc)\n", 2)

    # 5. disk image ---------------------------------------------------------------
    if not options.no_dmg:
        _step(logger, _("Disk image"))
        apps_link = os.path.join(stage_dir, "Applications")
        os.symlink("/Applications", apps_link)
        res = _run(["hdiutil", "create", "-volname", "%s %s" % (name, version),
                    "-srcfolder", stage_dir, "-fs", "HFS+", "-format", "ULMO",
                    "-ov", dmg])
        os.remove(apps_link)
        if res.returncode != 0:
            raise src.SatException(_("hdiutil create failed:\n%s") % res.stderr)

    shutil.move(app, app_final)

    logger.write("\n", 2)
    src.printcolors.print_value(logger, "Bundle", app_final, 2)
    if not options.no_dmg:
        src.printcolors.print_value(logger, "Disk image", dmg, 2)
    return 1 if problems else 0
