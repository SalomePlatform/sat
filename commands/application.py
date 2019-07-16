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
import stat
import sys
import shutil
import subprocess
import getpass

from src import ElementTree as etree
import src

parser = src.options.Options()
parser.add_option('n', 'name', 'string', 'name',
    _('Optional: The name of the application (default is APPLICATION.virtual_app.name or '
      'runAppli)'))
parser.add_option('c', 'catalog', 'string', 'catalog',
    _('Optional: The resources catalog to use'))
parser.add_option('t', 'target', 'string', 'target',
    _('Optional: The directory where to create the application (default is '
      'APPLICATION.workdir)'))
parser.add_option('', 'gencat', 'string', 'gencat',
    _("Optional: Create a resources catalog for the specified machines "
      "(separated with ',')\n\tNOTICE: this command will ssh to retrieve "
      "information to each machine in the list"))
parser.add_option('m', 'module', 'list2', 'modules',
    _("Optional: the restricted list of module(s) to include in the "
      "application"))
parser.add_option('', 'use_mesa', 'boolean', 'use_mesa',
    _("Optional: Create a launcher that will use mesa products\n\t"
      "It can be usefull whan salome is used on a remote machine through ssh"))

##
# Creates an alias for runAppli.
def make_alias(appli_path, alias_path, force=False):
    assert len(alias_path) > 0, "Bad name for alias"
    if os.path.exists(alias_path) and not force:
        raise src.SatException(_("Cannot create the alias '%s'\n") % alias_path)
    else: # find relative path
        os.symlink(appli_path, alias_path)

##
# add the definition of a module to out stream.
def add_module_to_appli(out, module, has_gui, module_path, logger, flagline):
    if not os.path.exists(module_path):
        if not flagline:
            logger.write("\n", 3, False)
            flagline = True
        logger.write("  " + src.printcolors.printcWarning(_(
                        "WARNING: module %s not installed") % module) + "\n", 3)

    out.write('   <module name="%s" gui="%s" path="%s"/>\n' % (module,
                                                               has_gui,
                                                               module_path))
    return flagline

##
# Creates the config file to create an application with the list of modules.
def create_config_file(config, modules, env_files, logger):

    samples = ""
    if 'SAMPLES' in config.APPLICATION.products:
        samples = src.product.get_product_config(config, 'SAMPLES').source_dir

    config_file = src.get_tmp_filename(config, "appli_config.xml")
    f = open(config_file, "w")

    f.write('<application>\n')
    for env_file in env_files:
        if env_file.endswith("cfg"):
            f.write('<context path="%s"/>\n' % env_file)
        else:   
            f.write('<prerequisites path="%s"/>\n' % env_file)

    f.write('<resources path="CatalogResources.xml"/>\n')
    f.write('<modules>\n')

    flagline = False
    for m in modules:
        mm = src.product.get_product_config(config, m)
        # do not include in virtual application application module!
        if src.get_property_in_product_cfg(mm, "is_salome_application") == "yes":
            continue
        # do not include products that do not compile
        if not src.product.product_compiles(mm):
            continue
        #obsolete?
        if src.product.product_is_smesh_plugin(mm):
            continue

        if 'install_dir' in mm and bool(mm.install_dir):
            if src.product.product_is_cpp(mm):
                # cpp module
                for aa in src.product.get_product_components(mm):
                    install_dir=os.path.join(config.APPLICATION.workdir,
                                             config.INTERNAL.config.install_dir)
                    mp = os.path.join(install_dir, aa)
                    flagline = add_module_to_appli(f,
                                                   aa,
                                                   "yes",
                                                   mp,
                                                   logger,
                                                   flagline)
            else:
                # regular module
                mp = mm.install_dir
                gui = src.get_cfg_param(mm, "has_gui", "yes")
                flagline = add_module_to_appli(f, m, gui, mp, logger, flagline)

    f.write('</modules>\n')
    f.write('<samples path="%s"/>\n' % samples)
    f.write('</application>\n')
    f.close()

    return config_file

##
# Customizes the application by editing SalomeApp.xml.
def customize_app(config, appli_dir, logger):
    if 'configure' not in config.APPLICATION.virtual_app \
        or len(config.APPLICATION.virtual_app.configure) == 0:
        return

    # shortcut to get an element (section or parameter) from parent.
    def get_element(parent, name, strtype):
        for c in parent.getchildren():
            if c.attrib['name'] == name:
                return c

        # element not found create it
        elt = add_simple_node(parent, strtype)
        elt.attrib['name'] = name
        return elt

    # shortcut method to create a node
    def add_simple_node(parent, node_name, text=None):
        n = etree.Element(node_name)
        if text is not None:
            try:
                n.text = text.strip("\n\t").decode("UTF-8")
            except:
                sys.stderr.write("################ %s %s\n" % (node_name, text))
                n.text = "?"
        parent.append(n)
        return n

    # read the app file
    app_file = os.path.join(appli_dir, "SalomeApp.xml")
    tree = etree.parse(app_file)
    document = tree.getroot()
    assert document is not None, "document tag not found"

    logger.write("\n", 4)
    for section_name in config.APPLICATION.virtual_app.configure:
        for parameter_name in config.APPLICATION.virtual_app.configure[section_name]:
            parameter_value = config.APPLICATION.virtual_app.configure[section_name][parameter_name]
            logger.write("  configure: %s/%s = %s\n" % (section_name,
                                                        parameter_name,
                                                        parameter_value), 4)
            section = get_element(document, section_name, "section")
            parameter = get_element(section, parameter_name, "parameter")
            parameter.attrib['value'] = parameter_value

    # write the file
    f = open(app_file, "w")
    f.write("<?xml version='1.0' encoding='utf-8'?>\n")
    f.write(etree.tostring(document, encoding='utf-8'))
    f.close()

##
# Generates the application with the config_file.
def generate_application(config, appli_dir, config_file, logger):
    target_dir = os.path.dirname(appli_dir)

    install_KERNEL_dir = src.product.get_product_config(config,
                                                        'KERNEL').install_dir
    script = os.path.join(install_KERNEL_dir, "bin", "salome", "appli_gen.py")
    if not os.path.exists(script):
        raise src.SatException(_("KERNEL is not installed"))
    
    # Add SALOME python in the environment in order to avoid python version 
    # problems at appli_gen.py call
    if 'Python' in config.APPLICATION.products:
        envi = src.environment.SalomeEnviron(config,
                                             src.environment.Environ(
                                                              dict(os.environ)),
                                             True)
        envi.set_a_product('Python', logger)
    
    command = "python %s --prefix=%s --config=%s" % (script,
                                                     appli_dir,
                                                     config_file)
    logger.write("\n>" + command + "\n", 5, False)
    res = subprocess.call(command,
                    shell=True,
                    cwd=target_dir,
                    env=envi.environ.environ,
                    stdout=logger.logTxtFile,
                    stderr=subprocess.STDOUT)
    
    if res != 0:
        raise src.SatException(_("Cannot create application, code = %d\n") % res)

    return res

##
#
def write_step(logger, message, level=3, pad=50):
    logger.write("%s %s " % (message, '.' * (pad - len(message.decode("UTF-8")))), level)
    logger.flush()

##
# Creates a SALOME application.
def create_application(config, appli_dir, catalog, logger, display=True):
      
    SALOME_modules = get_SALOME_modules(config)
    
    warn = ['KERNEL', 'GUI']
    if display:
        for w in warn:
            if w not in SALOME_modules:
                msg = _("WARNING: module %s is required to create application\n") % w
                logger.write(src.printcolors.printcWarning(msg), 2)

    # generate the launch file
    retcode = generate_launch_file(config,
                                   appli_dir,
                                   catalog,
                                   logger,
                                   SALOME_modules)
    
    if retcode == 0:
        cmd = src.printcolors.printcLabel("%s/salome" % appli_dir)

    if display:
        logger.write("\n", 3, False)
        logger.write(_("To launch the application, type:\n"), 3, False)
        logger.write("  %s" % (cmd), 3, False)
        logger.write("\n", 3, False)
    return retcode

def get_SALOME_modules(config):
    l_modules = []
    for product in config.APPLICATION.products:
        product_info = src.product.get_product_config(config, product)
        if (src.product.product_is_salome(product_info) or 
               src.product.product_is_generated(product_info)):
            l_modules.append(product)
    return l_modules

##
# Obsolescent way of creating the application.
# This method will use appli_gen to create the application directory.
def generate_launch_file(config, appli_dir, catalog, logger, l_SALOME_modules):
    retcode = -1

    if len(catalog) > 0 and not os.path.exists(catalog):
        raise IOError(_("Catalog not found: %s") % catalog)
    
    write_step(logger, _("Creating environment files"))
    status = src.KO_STATUS

    # build the application (the name depends upon salome version
    env_file = os.path.join(config.APPLICATION.workdir, "env_launch")
    VersionSalome = src.get_salome_version(config)
    if VersionSalome>=820:
        # for salome 8+ we use a salome context file for the virtual app
        app_shell=["cfg", "bash"]
        env_files=[env_file+".cfg", env_file+".sh"]
    else:
        app_shell=["bash"]
        env_files=[env_file+".sh"]

    try:
        import environ
        # generate only shells the user wants (by default bash, csh, batch)
        # the environ command will only generate file compatible 
        # with the current system.
        environ.write_all_source_files(config,
                                       logger,
                                       shells=app_shell,
                                       silent=True)
        status = src.OK_STATUS
    finally:
        logger.write(src.printcolors.printc(status) + "\n", 2, False)


    write_step(logger, _("Building application"), level=2)
    cf = create_config_file(config, l_SALOME_modules, env_files, logger)

    # create the application directory
    os.makedirs(appli_dir)

    # generate the application
    status = src.KO_STATUS
    try:
        retcode = generate_application(config, appli_dir, cf, logger)
        customize_app(config, appli_dir, logger)
        status = src.OK_STATUS
    finally:
        logger.write(src.printcolors.printc(status) + "\n", 2, False)

    # copy the catalog if one
    if len(catalog) > 0:
        shutil.copy(catalog, os.path.join(appli_dir, "CatalogResources.xml"))

    return retcode



##
# Generates the catalog from a list of machines.
def generate_catalog(machines, config, logger):
    # remove empty machines
    machines = map(lambda l: l.strip(), machines)
    machines = filter(lambda l: len(l) > 0, machines)

    src.printcolors.print_value(logger,
                                _("Generate Resources Catalog"),
                                ", ".join(machines),
                                4)
    cmd = '"cat /proc/cpuinfo | grep MHz ; cat /proc/meminfo | grep MemTotal"'
    user = getpass.getuser()

    catfile = src.get_tmp_filename(config, "CatalogResources.xml")
    catalog = file(catfile, "w")
    catalog.write("<!DOCTYPE ResourcesCatalog>\n<resources>\n")
    for k in machines:
        if not src.architecture.is_windows(): 
            logger.write("    ssh %s " % (k + " ").ljust(20, '.'), 4)
            logger.flush()

            ssh_cmd = 'ssh -o "StrictHostKeyChecking no" %s %s' % (k, cmd)
            p = subprocess.Popen(ssh_cmd, shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            p.wait()

            machine_access = (p.returncode == 0) 
            if not machine_access:
                logger.write(src.printcolors.printc(src.KO_STATUS) + "\n", 4)
                logger.write("    " + src.printcolors.printcWarning(p.stderr.read()),
                             2)
            else:
                logger.write(src.printcolors.printc(src.OK_STATUS) + "\n", 4)
                lines = p.stdout.readlines()
                freq = lines[0][:-1].split(':')[-1].split('.')[0].strip()
                nb_proc = len(lines) -1
                memory = lines[-1].split(':')[-1].split()[0].strip()
                memory = int(memory) / 1000

            catalog.write("    <machine\n")
            catalog.write("        protocol=\"ssh\"\n")
            catalog.write("        nbOfNodes=\"1\"\n")
            catalog.write("        mode=\"interactif\"\n")
            catalog.write("        OS=\"LINUX\"\n")

            if (not src.architecture.is_windows()) and machine_access:
                catalog.write("        CPUFreqMHz=\"%s\"\n" % freq)
                catalog.write("        nbOfProcPerNode=\"%s\"\n" % nb_proc)
                catalog.write("        memInMB=\"%s\"\n" % memory)

            catalog.write("        userName=\"%s\"\n" % user)
            catalog.write("        name=\"%s\"\n" % k)
            catalog.write("        hostname=\"%s\"\n" % k)
            catalog.write("    >\n")
            catalog.write("    </machine>\n")

    catalog.write("</resources>\n")
    catalog.close()
    return catfile

##################################################

##
# Describes the command
def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the application command description.
    :rtype: str
    '''
    return _("The application command creates a SALOME application.\n"
             "WARNING: it works only for SALOME 6. Use the \"launcher\" "
             "command for newer versions of SALOME\n\nexample:\nsat application"
             " SALOME-6.6.0")

##
# Runs the command.
def run(args, runner, logger):
    '''method that is called when salomeTools is called with application
       parameter.
    '''
    
    (options, args) = parser.parse_args(args)

    # check for product
    src.check_config_has_application( runner.cfg )

    application = src.printcolors.printcLabel(runner.cfg.VARS.application)
    logger.write(_("Building application for %s\n") % application, 1)

    # if section APPLICATION.virtual_app does not exists create one
    if "virtual_app" not in runner.cfg.APPLICATION:
        msg = _("The section APPLICATION.virtual_app is not defined in the product.")
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    # get application dir
    target_dir = runner.cfg.APPLICATION.workdir
    if options.target:
        target_dir = options.target

    # set list of modules
    if options.modules:
        runner.cfg.APPLICATION.virtual_app['modules'] = options.modules

    # activate mesa use in the generated application
    if options.use_mesa:
        src.activate_mesa_property(runner.cfg)

    # set name and application_name
    if options.name:
        runner.cfg.APPLICATION.virtual_app['name'] = options.name
        runner.cfg.APPLICATION.virtual_app['application_name'] = options.name + "_appdir"
    
    application_name = src.get_cfg_param(runner.cfg.APPLICATION.virtual_app,
                                         "application_name",
                                         runner.cfg.APPLICATION.virtual_app.name + "_appdir")
    appli_dir = os.path.join(target_dir, application_name)

    src.printcolors.print_value(logger,
                                _("Application directory"),
                                appli_dir,
                                3)

    # get catalog
    catalog, catalog_src = "", ""
    if options.catalog:
        # use catalog specified in the command line
        catalog = options.catalog
    elif options.gencat:
        # generate catalog for given list of computers
        catalog_src = options.gencat
        catalog = generate_catalog(options.gencat.split(","),
                                   runner.cfg,logger)
    elif 'catalog' in runner.cfg.APPLICATION.virtual_app:
        # use catalog specified in the product
        if runner.cfg.APPLICATION.virtual_app.catalog.endswith(".xml"):
            # catalog as a file
            catalog = runner.cfg.APPLICATION.virtual_app.catalog
        else:
            # catalog as a list of computers
            catalog_src = runner.cfg.APPLICATION.virtual_app.catalog
            mlist = filter(lambda l: len(l.strip()) > 0,
                           runner.cfg.APPLICATION.virtual_app.catalog.split(","))
            if len(mlist) > 0:
                catalog = generate_catalog(runner.cfg.APPLICATION.virtual_app.catalog.split(","),
                                           runner.cfg, logger)

    # display which catalog is used
    if len(catalog) > 0:
        catalog = os.path.realpath(catalog)
        if len(catalog_src) > 0:
            src.printcolors.print_value(logger,
                                        _("Resources Catalog"),
                                        catalog_src,
                                        3)
        else:
            src.printcolors.print_value(logger,
                                        _("Resources Catalog"),
                                        catalog,
                                        3)

    logger.write("\n", 3, False)

    details = []

    # remove previous application
    if os.path.exists(appli_dir):
        write_step(logger, _("Removing previous application directory"))
        rres = src.KO_STATUS
        try:
            shutil.rmtree(appli_dir)
            rres = src.OK_STATUS
        finally:
            logger.write(src.printcolors.printc(rres) + "\n", 3, False)

    # generate the application
    try:
        try: # try/except/finally not supported in all version of python
            retcode = create_application(runner.cfg, appli_dir, catalog, logger)
        except Exception as exc:
            details.append(str(exc))
            raise
    finally:
        logger.write("\n", 3, False)

    return retcode

