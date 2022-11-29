#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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

import os
import sys
import shutil
import imp
import subprocess

import src
from  src.versionMinorMajorPatch import MinorMajorPatch as MMP
import src.debug as DBG

parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
                  _("Optional: the list of products to generate"))
parser.add_option('', 'yacsgen', 'string', 'yacsgen',
                  _("Optional: path to YACSGEN's module_generator package"))

def generate_component_list(config, product_name, product_info, context, logger):
    res = "?"
    logger.write("\n", 3)
    for compo in src.product.get_product_components(product_info):
        header = "  %s %s " % (src.printcolors.printcLabel(compo),
                               "." * (20 - len(compo)))
        res = generate_component(config,
                                 compo,
                                 product_name,
                                 product_info,
                                 context,
                                 header,
                                 logger)
        if config.USER.output_verbose_level == 3:
            logger.write("\r%s%s\r%s" % (header, " " * 20, header), 3)
        logger.write(src.printcolors.printc(res), 3, False)
        logger.write("\n", 3, False)
    return res

def generate_component(config, compo, product_name, product_info, context, header, logger):
#   get from config include file name and librairy name, or take default value
    if "hxxfile" in product_info:
        hxxfile = product_info.hxxfile
    else:
        hxxfile = compo + ".hxx"
    if "cpplib" in product_info:
        cpplib = product_info.cpplib
    else:
        cpplib = "lib" + compo + "CXX.so"
    cpp_path = product_info.install_dir

    logger.write("%s\n" % header, 4, False)
    src.printcolors.print_value(logger, "hxxfile", hxxfile, 4)
    src.printcolors.print_value(logger, "cpplib", cpplib, 4)
    src.printcolors.print_value(logger, "cpp_path", cpp_path, 4)

    # create a product_info at runtime
    compo_info = src.pyconf.Mapping(config)
    compo_info.name = compo
    compo_info.nb_proc = 1
    generate_dir = os.path.join(config.APPLICATION.workdir, "GENERATED")
    install_dir = os.path.join(config.APPLICATION.workdir, "INSTALL")
    build_dir = os.path.join(config.APPLICATION.workdir, "BUILD")
    compo_info.source_dir = os.path.join(generate_dir, compo + "_SRC")
    compo_info.install_dir = os.path.join(install_dir, compo)
    compo_info.build_dir = os.path.join(build_dir, compo)
    compo_info.depend = product_info.depend
    compo_info.depend.append(product_info.name, "") # add cpp module
    compo_info.opt_depend = product_info.opt_depend

    config.PRODUCTS.addMapping(compo, src.pyconf.Mapping(config), "")
    config.PRODUCTS[compo].default = compo_info

    builder = src.compilation.Builder(config, logger, product_name, compo_info, check_src=False)
    builder.header = header

    # generate the component
    # create GENERATE dir if necessary
    if not os.path.exists(generate_dir):
        os.mkdir(generate_dir)

    # delete previous generated directory if it already exists
    if os.path.exists(compo_info.source_dir):
        logger.write("  delete %s\n" % compo_info.source_dir, 4)
        shutil.rmtree(compo_info.source_dir)

    # generate generates in the current directory => change for generate dir
    curdir = os.curdir
    os.chdir(generate_dir)

    # inline class to override bootstrap method
    import module_generator
    class sat_generator(module_generator.Generator):
        # old bootstrap for automake (used if salome version <= 7.4)
        def bootstrap(self, source_dir, log_file):
            # replace call to default bootstrap() by using subprocess call (cleaner)
            command = "sh autogen.sh"
            ier = subprocess.call(command, shell=True, cwd=source_dir,
                                  stdout=log_file, stderr=subprocess.STDOUT)
            if ier != 0:
                raise src.SatException("bootstrap has ended in error")


    # determine salome version
    VersionSalome = src.get_salome_version(config)
    if VersionSalome >= MMP([7,5,0]) :
        use_autotools=False
        builder.log('USE CMAKE', 3)
    else:
        use_autotools=True
        builder.log('USE AUTOTOOLS', 3)

    result = "GENERATE"
    builder.log('GENERATE', 3)

    prevstdout = sys.stdout
    prevstderr = sys.stderr

    try:
        sys.stdout = logger.logTxtFile
        sys.stderr = logger.logTxtFile

        if src.product.product_is_mpi(product_info):
            salome_compo = module_generator.HXX2SALOMEParaComponent(hxxfile,
                                                                    cpplib,
                                                                    cpp_path)
        else:
            salome_compo = module_generator.HXX2SALOMEComponent(hxxfile,
                                                                cpplib,
                                                                cpp_path)

        if src.product.product_has_salome_gui(product_info):
            # get files to build a template GUI
            try: # try new yacsgen api
                gui_files = salome_compo.getGUIfilesTemplate(compo)
            except:  # use old yacsgen api
                gui_files = salome_compo.getGUIfilesTemplate()
        else:
            gui_files = None

        mg = module_generator.Module(compo, components=[salome_compo],
                                     prefix=generate_dir, gui=gui_files)
        g = sat_generator(mg, context)
        g.generate()

        if use_autotools:
            result = "BUID_CONFIGURE"
            builder.log('BUID_CONFIGURE (no bootstrap)', 3)
            g.bootstrap(compo_info.source_dir, logger.logTxtFile)

        result = src.OK_STATUS
    finally:
        sys.stdout = prevstdout
        sys.stderr = prevstderr

    # go back to previous directory
    os.chdir(curdir)

    # do the compilation using the builder object
    if builder.prepare()!= 0: return "Error in prepare"
    if use_autotools:
        if builder.configure()!= 0: return "Error in configure"
    else:
        if builder.cmake()!= 0: return "Error in cmake"

    if builder.make(config.VARS.nb_proc, "")!=0: return "Error in make"
    if builder.install()!=0: return "Error in make install"

    # copy specified logo in generated component install directory
    # rem : logo is not copied in source dir because this would require
    #       to modify the generated makefile
    logo_path = src.product.product_has_logo(product_info)
    if logo_path:
        destlogo = os.path.join(compo_info.install_dir, "share", "salome",
            "resources", compo.lower(), compo + ".png")
        src.Path(logo_path).copyfile(destlogo)

    return result

def build_context(config, logger):
    products_list = [ 'KERNEL', 'GUI' ]
    ctxenv = src.environment.SalomeEnviron(config,
                                           src.environment.Environ(dict(
                                                                   os.environ)),
                                           True)
    ctxenv.silent = True
    ctxenv.set_full_environ(logger, config.APPLICATION.products.keys())

    dicdir = {}
    for p in products_list:
        prod_env = p + "_ROOT_DIR"
        val = os.getenv(prod_env)
        if os.getenv(prod_env) is None:
            if p not in config.APPLICATION.products:
                warn = _("product %(product)s is not defined. Include it in the"
                         " application or define $%(env)s.") % \
                    { "product": p, "env": prod_env}
                logger.write(src.printcolors.printcWarning(warn), 1)
                logger.write("\n", 3, False)
                val = ""
            val = ctxenv.environ.environ[prod_env]
        dicdir[p] = val

    # the dictionary requires all keys
    # but the generation requires only values for KERNEL and GUI
    context = {
        "update": 1,
        "makeflags": "-j2",
        "kernel": dicdir["KERNEL"],
        "gui":    dicdir["GUI"],
        "yacs":   "",
        "med":    "",
        "mesh":   "",
        "visu":   "",
        "geom":   "",
    }
    return context

def check_module_generator(directory=None):
    """Check if module_generator is available.

    :param directory str: The directory of YACSGEN.
    :return: The YACSGEN path if the module_generator is available, else None
    :rtype: str
    """
    undo = False
    if directory is not None and directory not in sys.path:
        sys.path.insert(0, directory)
        undo = True

    res = None
    try:
        #import module_generator
        info = imp.find_module("module_generator")
        res = info[1]
    except ImportError:
        if undo:
            sys.path.remove(directory)
        res = None

    return res

def check_yacsgen(config, directory, logger):
    """Check if YACSGEN is available.

    :param config Config: The global configuration.
    :param directory str: The directory given by option --yacsgen
    :param logger Logger: The logger instance
    :return: The path to yacsgen directory
    :rtype: str
    """
    # first check for YACSGEN (command option, then product, then environment)
    yacsgen_dir = None
    yacs_src = "?"
    if directory is not None:
        yacsgen_dir = directory
        yacs_src = _("Using YACSGEN from command line")
    elif 'YACSGEN' in config.APPLICATION.products:
        yacsgen_info = src.product.get_product_config(config, 'YACSGEN')
        yacsgen_dir = yacsgen_info.install_dir
        yacs_src = _("Using YACSGEN from application")
    elif "YACSGEN_ROOT_DIR" in os.environ:
        yacsgen_dir = os.getenv("YACSGEN_ROOT_DIR")
        yacs_src = _("Using YACSGEN from environment")

    if yacsgen_dir is None:
        return (False, _("The generate command requires YACSGEN."))

    logger.write("  %s\n" % yacs_src, 2, True)
    logger.write("  %s\n" % yacsgen_dir, 5, True)

    if not os.path.exists(yacsgen_dir):
        message = _("YACSGEN directory not found: '%s'") % yacsgen_dir
        return (False, _(message))

    # load module_generator
    c = check_module_generator(yacsgen_dir)
    if c is not None:
        return c

    pv = os.getenv("PYTHON_VERSION")
    if pv is None:
        python_info = src.product.get_product_config(config, "Python")
        pv = '.'.join(python_info.version.split('.')[:2])
    assert pv is not None, "$PYTHON_VERSION not defined"
    yacsgen_dir = os.path.join(yacsgen_dir, "lib", "python%s" % pv,
                               "site-packages")
    c = check_module_generator(yacsgen_dir)
    if c is not None:
        return c

    return (False,
            _("The python module module_generator was not found in YACSGEN"))


def description():
    '''method that is called when salomeTools is called with --help option.

    :return: The text to display for the generate command description.
    :rtype: str
    '''
    return _("The generate command generates SALOME modules from 'pure cpp' "
             "products.\nWARNING this command NEEDS YACSGEN to run!\n\nexample:"
             "\nsat generate SALOME-master --products FLICACPP")


def run(args, runner, logger):
    '''method that is called when salomeTools is called with generate parameter.
    '''

    # Check that the command has been called with an application
    src.check_config_has_application(runner.cfg)

    logger.write(_('Generation of SALOME modules for application %s\n') % \
        src.printcolors.printcLabel(runner.cfg.VARS.application), 1)

    (options, args) = parser.parse_args(args)

    status = src.KO_STATUS

    # verify that YACSGEN is available
    yacsgen_dir = check_yacsgen(runner.cfg, options.yacsgen, logger)

    if isinstance(yacsgen_dir, tuple):
        # The check failed
        __, error = yacsgen_dir
        msg = _("Error: %s" % error)
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    # Make the generator module visible by python
    sys.path.insert(0, yacsgen_dir)

    src.printcolors.print_value(logger, _("YACSGEN dir"), yacsgen_dir, 3)
    logger.write("\n", 2)
    products = runner.cfg.APPLICATION.products
    if options.products:
        products = options.products

    details = []
    nbgen = 0

    context = build_context(runner.cfg, logger)
    for product in products:
        header = _("Generating %s") % src.printcolors.printcLabel(product)
        header += " %s " % ("." * (20 - len(product)))
        logger.write(header, 3)
        logger.flush()

        if product not in runner.cfg.PRODUCTS:
            logger.write(_("Unknown product\n"), 3, False)
            continue

        pi = src.product.get_product_config(runner.cfg, product)
        if not src.product.product_is_generated(pi):
            logger.write(_("not a generated product\n"), 3, False)
            continue

        logger.write(_("\nCleaning generated directories\n"), 3, False)
        # clean source, build and install directories of the generated product
        # no verbosity to avoid warning at the first generation, for which dirs don't exist
        runner.clean(runner.cfg.VARS.application +
                  " --products " + pi.name +
                  " --generated",
                  batch=True,
                  verbose=0,
                  logger_add_link = logger)
        nbgen += 1
        try:
            result = generate_component_list(runner.cfg,
                                             product,
                                             pi,
                                             context,
                                             logger)
        except Exception as exc:
            result = str(exc)

        if result != src.OK_STATUS:
            result = _("ERROR: %s") % result
            details.append([product, result])

    if len(details) == 0:
        status = src.OK_STATUS
    else: #if config.USER.output_level != 3:
        logger.write("\n", 2, False)
        logger.write(_("The following modules were not generated correctly:\n"), 2)
        for d in details:
            logger.write("  %s: %s\n" % (d[0], d[1]), 2, False)
    logger.write("\n", 2, False)

    if status == src.OK_STATUS:
        return 0
    return len(details)
