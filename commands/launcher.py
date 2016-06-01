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

parser = src.options.Options()

parser.add_option('n', 'name', 'string', 'name', _('The name of the launcher '
                            '(default is APPLICATION.profile.launcher_name)'))
parser.add_option('c', 'catalog', 'string', 'catalog',
    _('The resources catalog to use'))
parser.add_option('', 'gencat', 'string', 'gencat',
    _("Create a resources catalog for the specified machines "
      "(separated with ',') \n\tNOTICE: this command will ssh to retrieve"
      " information to each machine in the list"))

def generate_launch_file(config,
                         logger,
                         env_info=None,
                         pathlauncher=None,
                         display=True,
                         additional_env={}):
    '''Generates the launcher file.
    
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param env_info str: The list of products to add in the files.
    :param pathlauncher str: The path to the launcher to generate
    :param src_root str: The path to the directory where the sources are
    :param display boolean: If False, do not print anything in the terminal
    :param additional_env dict: The dict giving additional 
                                environment variables
    :return: The launcher file path.
    :rtype: str
    '''
    # Get the application directory and the profile directory
    out_dir = config.APPLICATION.workdir
    profile = config.APPLICATION.profile
    profile_install_dir = get_profile_dir(config)
    
    # Compute the default launcher path if it is not provided in pathlauncher
    # parameter
    if pathlauncher is None:
        filepath = os.path.join( os.path.join( profile_install_dir,
                                               'bin',
                                               'salome' ),
                                 profile['launcher_name'] )
    else:
        filepath = os.path.join(pathlauncher, profile['launcher_name'])

    # Remove the file if it exists in order to replace it
    if os.path.exists(filepath):
        os.remove(filepath)

    # Add the APPLI variable
    additional_env['APPLI'] = filepath

    # Get the launcher template
    withProfile = src.fileEnviron.withProfile.replace( "PROFILE_INSTALL_DIR",
                                                       profile_install_dir )
    before, after = withProfile.split(
                                "# here your local standalone environment\n")

    # create an environment file writer
    writer = src.environment.FileEnvWriter(config,
                                           logger,
                                           out_dir,
                                           src_root=None,
                                           env_info=env_info)

    # Display some information
    if display:
        # Write the launcher file
        logger.write(_("Generating launcher for %s :\n") % 
                     src.printcolors.printcLabel(config.VARS.application), 1)
        logger.write("  %s\n" %src.printcolors.printcLabel(filepath), 1)
    
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

def generate_launch_link(config,
                         logger,
                         launcherPath,
                         pathlauncher=None,
                         display=True,
                         packageLauncher=False):
    '''Generates the launcher link that sources Python 
       and call the actual launcher.
    
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param launcherPath str: The path to the launcher to call
    :param pathlauncher str: The path to the launcher (link) to generate
    :param display boolean: If False, do not print anything in the terminal
    :param packageLauncher boolean: if True, use a relative path (for package)
    :return: The launcher link file path.
    :rtype: str
    '''
    if pathlauncher is None:
        # Make an executable file that sources python, then launch the launcher
        # produced by generate_launch_file method
        sourceLauncher = os.path.join(config.APPLICATION.workdir,
                                      config.APPLICATION.profile.launcher_name)
    else:
        sourceLauncher = os.path.join(pathlauncher,
                                      config.APPLICATION.profile.launcher_name)

    # Change the extension for the windows case
    if platform.system() == "Windows" :
            sourceLauncher += '.bat'

    # display some information
    if display:
        logger.write(_("\nGenerating the executable that sources"
                       " python and runs the launcher :\n") , 1)
        logger.write("  %s\n" %src.printcolors.printcLabel(sourceLauncher), 1)

    # open the file to write
    f = open(sourceLauncher, "w")

    # Write the set up of the environment
    if platform.system() == "Windows" :
        shell = 'bat'
    else:
        shell = 'bash'
        
    # Write the Python environment files
    env = src.environment.SalomeEnviron( config, 
                        src.fileEnviron.get_file_environ( f, shell, config ) )
    env.set_a_product( "Python", logger)

    # Write the call to the original launcher
    f.write( "\n\n")
    if packageLauncher:
        cmd = os.path.join('${out_dir_Path}', launcherPath)
    else:
        cmd = launcherPath

    if platform.system() == "Windows" :
        cmd = 'python ' + cmd + ' %*'
    else:
        cmd = cmd + ' $*'
    
    f.write( cmd )
    f.write( "\n\n")

    # Write the cleaning of the environment
    env.finish(True)

    # Close new launcher
    f.close()
    os.chmod(sourceLauncher,
             stat.S_IRUSR |
             stat.S_IRGRP |
             stat.S_IROTH |
             stat.S_IWUSR |
             stat.S_IWGRP |
             stat.S_IWOTH |
             stat.S_IXUSR |
             stat.S_IXGRP |
             stat.S_IXOTH)
    return sourceLauncher

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
    # Compute the location where to copy the file
    profile_dir = get_profile_dir(config)
    new_catalog_path = os.path.join(profile_dir, "CatalogResources.xml")
    # Do the copy
    shutil.copy(catalog_path, new_catalog_path)
    additional_environ = {'USER_CATALOG_RESOURCES_FILE' : new_catalog_path}
    return additional_environ

def get_profile_dir(config):
    """Get the profile directory from the config
    
    :param config Config: The global configuration
    :return: The profile install directory
    :rtype: Str
    """
    profile_name = config.APPLICATION.profile.product
    profile_info = src.product.get_product_config(config, profile_name)
    return profile_info.install_dir

def finish_profile_install(config, launcherPath):
    """Add some symlinks required for SALOME
    
    :param config Config: The global configuration
    :param launcherPath str: the launcher file path
    """
    # Create a USERS directory
    profile_dir = get_profile_dir(config)
    user_dir = os.path.join(profile_dir, 'USERS')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    # change rights of USERS directory
    os.chmod(user_dir,
             stat.S_IRUSR |
             stat.S_IRGRP |
             stat.S_IROTH |
             stat.S_IWUSR |
             stat.S_IWGRP |
             stat.S_IWOTH |
             stat.S_IXUSR |
             stat.S_IXGRP |
             stat.S_IXOTH)

    # create a link in root directory to the launcher
    if platform.system() != "Windows" :
        link_path = os.path.join(config.APPLICATION.workdir, 'salome')
        if not os.path.exists(link_path):
            try:
                os.symlink(launcherPath, link_path)
            except OSError:
                os.remove(link_path)
                os.symlink(launcherPath, link_path)

        link_path = os.path.join(profile_dir, 'salome')
        if not os.path.exists(link_path):
            try:
                os.symlink(launcherPath, link_path)
            except OSError:
                os.remove(link_path)
                os.symlink(launcherPath, link_path)

##################################################

##
# Describes the command
def description():
    return _("The launcher command generates a salome launcher.")

##
# Runs the command.
def run(args, runner, logger):

    # check for product
    (options, args) = parser.parse_args(args)

    # Verify that the command was called with an application
    src.check_config_has_application( runner.cfg )
    
    # Verify that the APPLICATION section has a profile section
    src.check_config_has_profile( runner.cfg )

    # Change the name of the file to create 
    # if the corresponding option was called
    if options.name:
        runner.cfg.APPLICATION.profile['launcher_name'] = options.name

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

    # Generate the launcher
    launcherPath = generate_launch_file( runner.cfg,
                                         logger,
                                         additional_env = additional_environ )

    # Create the link (bash file that sources python and then call 
    # the actual launcher) to the launcher
    generate_launch_link( runner.cfg, logger, launcherPath)

    # Add some links
    finish_profile_install(runner.cfg, launcherPath)

    return 0
