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
                            ' launcher (default is '
                            'APPLICATION.profile.launcher_name)'))
parser.add_option('c', 'catalog', 'string', 'catalog',
    _('Optional: The resources catalog to use'))
parser.add_option('', 'gencat', 'string', 'gencat',
    _("Optional: Create a resources catalog for the specified machines "
      "(separated with ',') \n\tNOTICE: this command will ssh to retrieve"
      " information to each machine in the list"))
parser.add_option('', 'use_mesa', 'boolean', 'use_mesa',
    _("Optional: Create a launcher that will use mesa products\n\t"
      "It can be usefull whan salome is used on a remote machine through ssh"))

def generate_launch_file(config,
                         logger,
                         launcher_name,
                         pathlauncher,
                         display=True,
                         additional_env={}):
    '''Generates the launcher file.
    
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param launcher_name str: The name of the launcher to generate
    :param pathlauncher str: The path to the launcher to generate
    :param display boolean: If False, do not print anything in the terminal
    :param additional_env dict: The dict giving additional 
                                environment variables
    :return: The launcher file path.
    :rtype: str
    '''
    
    # Compute the default launcher path if it is not provided in pathlauncher
    # parameter
    filepath = os.path.join(pathlauncher, launcher_name)

    # Remove the file if it exists in order to replace it
    if os.path.exists(filepath):
        os.remove(filepath)

    # Add the APPLI variable
    additional_env['APPLI'] = filepath


    # get KERNEL bin installation path 
    # (in order for the launcher to get python salomeContext API)
    kernel_cfg = src.product.get_product_config(config, "KERNEL")
    if not src.product.check_installation(kernel_cfg):
        raise src.SatException(_("KERNEL is not installed"))
    kernel_root_dir = kernel_cfg.install_dir

    # set kernel bin dir (considering fhs property)
    if src.get_property_in_product_cfg(kernel_cfg, "fhs"):
        bin_kernel_install_dir = os.path.join(kernel_root_dir,"bin") 
    else:
        bin_kernel_install_dir = os.path.join(kernel_root_dir,"bin","salome") 

    # Get the launcher template
    withProfile = src.fileEnviron.withProfile\
                     .replace("BIN_KERNEL_INSTALL_DIR", bin_kernel_install_dir)\
                     .replace("KERNEL_INSTALL_DIR", kernel_root_dir)

    before, after = withProfile.split(
                                "# here your local standalone environment\n")

    # create an environment file writer
    writer = src.environment.FileEnvWriter(config,
                                           logger,
                                           pathlauncher,
                                           src_root=None,
                                           env_info=None)

    # Display some information
    if display:
        # Write the launcher file
        logger.write(_("Generating launcher for %s :\n") % 
                     src.printcolors.printcLabel(config.VARS.application), 1)
        logger.write("  %s\n" % src.printcolors.printcLabel(filepath), 1)
    
    # open the file and write into it
    launch_file = open(filepath, "w")
    launch_file.write(before)
    # Write
    writer.write_cfgForPy_file(launch_file, additional_env=additional_env)
    launch_file.write(after)
    launch_file.close()
    
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
    catalog = file(catfile, "w")
    
    # Write into it
    catalog.write("<!DOCTYPE ResourcesCatalog>\n<resources>\n")
    for k in machines:
        logger.write("    ssh %s " % (k + " ").ljust(20, '.'), 4)
        logger.flush()

        # Verify that the machine is accessible
        ssh_cmd = 'ssh -o "StrictHostKeyChecking no" %s %s' % (k, cmd)
        p = subprocess.Popen(ssh_cmd, shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        p.wait()

        if p.returncode != 0: # The machine is not accessible
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
    if options.name:
        launcher_name = options.name
    else:
        launcher_name = src.get_launcher_name(runner.cfg)

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

    # Generate the launcher
    launcherPath = generate_launch_file( runner.cfg,
                                         logger,
                                         launcher_name,
                                         launcher_path,
                                         additional_env = additional_environ )

    return 0
