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
import platform
import shutil
import getpass
import subprocess
import stat

import src
import src.debug as DBG

parser = src.options.Options()

parser.add_option('n', 'name', 'string', 'name', _('Optional: The name of the'
                  ' launcher (default is APPLICATION.profile.launcher_name)'))
parser.add_option('e', 'exe', 'string', 'path_exe', _('Use this option to generate a launcher which sets'
                  ' the environment and call the executable given as argument'
                  ' (its relative path to application workdir, or an exe name present in appli PATH)'))
parser.add_option('p', 'products', 'list2', 'products',
    _("Optional: Includes only the specified products."))
parser.add_option('c', 'catalog', 'string', 'catalog',
                  _('Optional: The resources catalog to use'))
parser.add_option('', 'gencat', 'string', 'gencat',
                  _("Optional: Create a resources catalog for the specified machines "
                  "(separated with ',') \n\tNOTICE: this command will ssh to retrieve"
                  " information to each machine in the list"))
parser.add_option('', 'use_mesa', 'boolean', 'use_mesa',
                  _("Optional: Create a launcher that will use mesa products\n\t"
                  "It can be usefull whan salome is used on a remote machine through ssh"))
parser.add_option('', 'no_path_init', 'boolean', 'no_path_init',
                 _("Optional: Create a launcher that will not reinitilise all path variables\n\t"
                   "By default only PATH is not reinitialised (its value is inherited from "
                   "user's environment)\n\tUse no_path_init option to suppress the reinitilisation"
                   " of every paths (LD_LIBRARY_PATH, PYTHONPATH, ...)"))


def generate_launch_file(config,
                         logger,
                         launcher_name,
                         pathlauncher,
                         path_exe,
                         env_info,
                         display=True,
                         additional_env={},
                         no_path_init=False):
    '''Generates the launcher file.
    
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param launcher_name str: The name of the launcher to generate
    :param path_exe str: The executable to use (either a relative path to 
                         application workdir, or an exe name in the path)
    :param pathlauncher str: The path to the launcher to generate
    :param display boolean: If False, do not print anything in the terminal
    :param additional_env dict: The dict giving additional 
                                environment variables
    :param env_info str: The list of products to add in the files.
    :return: The launcher file path.
    :rtype: str
    '''
    # build the launcher path, delete it if it exists
    filepath = os.path.join(pathlauncher, launcher_name)
    if os.path.exists(filepath):
        os.remove(filepath)
    kernel_root_dir=None
    cmd=None
    salome_application_name=None
    app_root_dir=None

    if path_exe:
        #case of a launcher based upon an executable
        
        if os.path.basename(path_exe) != path_exe:
            # for a relative (to workdir) path 
            # build absolute path of exe and check it
            exepath=os.path.join(config.APPLICATION.workdir, path_exe)
            if not os.path.exists(exepath):
                raise src.SatException(_("cannot find executable given : %s" % exepath))
        else:
            exepath=path_exe 

        # select the shell for the launcher (bast/bat)
        # and build the command used to launch the exe
        if src.architecture.is_windows():
            shell="bat"
            cmd="\n\nrem Launch exe with user arguments\n%s " % exepath + "%*"
        else:
            shell="bash"
            cmd='\n\n# Launch exe with user arguments\n%s "$*"' % exepath

    else:
        #case of a salome python2/3 launcher
        shell="cfgForPy"

        # get KERNEL bin installation path 
        # (in order for the launcher to get python salomeContext API)
        kernel_cfg = src.product.get_product_config(config, "KERNEL")
        if not src.product.check_installation(config, kernel_cfg):
            raise src.SatException(_("KERNEL is not installed"))
        kernel_root_dir = kernel_cfg.install_dir
        # set kernel bin dir (considering fhs property)
        if src.get_property_in_product_cfg(kernel_cfg, "fhs"):
            bin_kernel_install_dir = os.path.join(kernel_root_dir,"bin") 
        else:
            bin_kernel_install_dir = os.path.join(kernel_root_dir,"bin","salome") 

        # Add two sat variables used by fileEnviron to choose the right launcher header 
        # and do substitutions
        additional_env['sat_bin_kernel_install_dir'] = bin_kernel_install_dir
        if "python3" in config.APPLICATION and config.APPLICATION.python3 == "yes":
            additional_env['sat_python_version'] = 3
        else:
            additional_env['sat_python_version'] = 2

    # check if the application contains an application module
    l_product_info = src.product.get_products_infos(config.APPLICATION.products.keys(),
                                                    config)
    for prod_name, prod_info in l_product_info:
        # look for a salome application
        if src.get_property_in_product_cfg(prod_info, "is_salome_application") == "yes":
            # if user choose -p option (env_info not None), the set appli name only if product was selected.
            if env_info == None or ( prod_name in env_info):
                salome_application_name=prod_info.install_dir
            continue

    # if the application contains an application module, we set ABSOLUTE_APPLI_PATH to it.
    # if not we set it to KERNEL_INSTALL_DIR, which is sufficient, except for salome test
    if salome_application_name:
        app_root_dir=salome_application_name
    elif kernel_root_dir:
        app_root_dir=kernel_root_dir

    # Add the APPLI and ABSOLUTE_APPLI_PATH variable
    additional_env['APPLI'] = filepath
    if app_root_dir:
        additional_env['ABSOLUTE_APPLI_PATH'] = app_root_dir

    # create an environment file writer
    writer = src.environment.FileEnvWriter(config,
                                           logger,
                                           pathlauncher,
                                           None,
                                           env_info)

    # Display some information
    if display:
        # Write the launcher file
        logger.write(_("Generating launcher for %s :\n") % 
                     src.printcolors.printcLabel(config.VARS.application), 1)
        logger.write("  %s\n" % src.printcolors.printcLabel(filepath), 1)
    
    # Write the launcher
    writer.write_env_file(filepath, 
                          False,  # for launch
                          shell,
                          additional_env=additional_env,
                          no_path_init=no_path_init)
    

    # ... and append the launch of the exe 
    if cmd:
        with open(filepath, "a") as exe_launcher:
            exe_launcher.write(cmd)

    # change the rights in order to make the file executable for everybody
    os.chmod(filepath,
             stat.S_IRUSR |
             stat.S_IRGRP |
             stat.S_IROTH |
             stat.S_IWUSR |
             stat.S_IXUSR |
             stat.S_IXGRP |
             stat.S_IXOTH)
    return filepath


def generate_catalog(machines, config, logger):
    """Generates an xml catalog file from a list of machines.
    
    :param machines List: The list of machines to add in the catalog   
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :return: The catalog file path.
    :rtype: str
    """
    # remove empty machines
    machines = map(lambda l: l.strip(), machines)
    machines = filter(lambda l: len(l) > 0, machines)
    
    # log something
    src.printcolors.print_value(logger, _("Generate Resources Catalog"),
                                ", ".join(machines), 4)
    
    # The command to execute on each machine in order to get some information
    cmd = '"cat /proc/cpuinfo | grep MHz ; cat /proc/meminfo | grep MemTotal"'
    user = getpass.getuser()

    # Create the catalog path
    catfile = src.get_tmp_filename(config, "CatalogResources.xml")
    with open(catfile, 'w') as catalog:
        # Write into it
        catalog.write("<!DOCTYPE ResourcesCatalog>\n<resources>\n")
        for k in machines:
            if not src.architecture.is_windows(): 
                logger.write("    ssh %s " % (k + " ").ljust(20, '.'), 4)
                logger.flush()

                # Verify that the machine is accessible
                ssh_cmd = 'ssh -o "StrictHostKeyChecking no" %s %s' % (k, cmd)
                p = subprocess.Popen(ssh_cmd, shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                p.wait()

                machine_access = (p.returncode == 0) 
                if not machine_access: # The machine is not accessible
                    logger.write(src.printcolors.printc(src.KO_STATUS) + "\n", 4)
                    logger.write("    " + 
                                 src.printcolors.printcWarning(p.stderr.read()), 2)
                else:
                    # The machine is accessible, write the corresponding section on
                    # the xml file
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

            if (not src.architecture.is_windows()) and machine_access :
                catalog.write("        CPUFreqMHz=\"%s\"\n" % freq)
                catalog.write("        nbOfProcPerNode=\"%s\"\n" % nb_proc)
                catalog.write("        memInMB=\"%s\"\n" % memory)

            catalog.write("        userName=\"%s\"\n" % user)
            catalog.write("        name=\"%s\"\n" % k)
            catalog.write("        hostname=\"%s\"\n" % k)
            catalog.write("    >\n")
            catalog.write("    </machine>\n")

        catalog.write("</resources>\n")
    return catfile

def copy_catalog(config, catalog_path):
    """Copy the xml catalog file into the right location
    
    :param config Config: The global configuration
    :param catalog_path str: the catalog file path
    :return: The environment dictionary corresponding to the file path.
    :rtype: Dict
    """
    # Verify the existence of the file
    if not os.path.exists(catalog_path):
        raise IOError(_("Catalog not found: %s") % catalog_path)
    # Get the application directory and copy catalog inside
    out_dir = config.APPLICATION.workdir
    new_catalog_path = os.path.join(out_dir, "CatalogResources.xml")
    # Do the copy
    if catalog_path != new_catalog_path:
        shutil.copy(catalog_path, new_catalog_path)
    additional_environ = {'USER_CATALOG_RESOURCES_FILE' : new_catalog_path}
    return additional_environ



##################################################

##
# Describes the command
def description():
    return _("The launcher command generates a SALOME launcher.\n\nexample:"
             "\nsat launcher SALOME-master")

##
# Runs the command.
def run(args, runner, logger):

    # check for product
    (options, args) = parser.parse_args(args)

    # Verify that the command was called with an application
    src.check_config_has_application( runner.cfg )
    
    # Determine the launcher name (from option, profile section or by default "salome")
    if options.products is None:
        environ_info = None
    else:
        # add products specified by user (only products 
        # included in the application)
        environ_info = filter(lambda l:
                              l in runner.cfg.APPLICATION.products.keys(),
                              options.products)
    if options.name:
        launcher_name = options.name
    else:
        launcher_name = src.get_launcher_name(runner.cfg)

    no_path_initialisation=False
    if options.no_path_init:
        no_path_initialisation = True
        
    # set the launcher path
    launcher_path = runner.cfg.APPLICATION.workdir

    # Copy a catalog if the option is called
    additional_environ = {}
    if options.catalog:
        additional_environ = copy_catalog(runner.cfg, options.catalog)

    # Generate a catalog of resources if the corresponding option was called
    if options.gencat:
        catalog_path  = generate_catalog(options.gencat.split(","),
                                         runner.cfg,
                                         logger)
        additional_environ = copy_catalog(runner.cfg, catalog_path)

    # activate mesa use in the generated launcher
    if options.use_mesa:
        src.activate_mesa_property(runner.cfg)

    # option -e has precedence over section profile
    if not options.path_exe and src.get_launcher_exe(runner.cfg):
        options.path_exe=src.get_launcher_exe(runner.cfg)

    # Generate the launcher
    generate_launch_file(runner.cfg,
                         logger,
                         launcher_name,
                         launcher_path,
                         options.path_exe,
                         additional_env = additional_environ,
                         env_info=environ_info,
                         no_path_init = no_path_initialisation )

    return 0
