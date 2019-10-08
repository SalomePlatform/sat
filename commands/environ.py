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

import src

parser = src.options.Options()
parser.add_option('', 'shell', 'list2', 'shell',
    _("Optional: Generates the environment files for the given format: "
      "bash (default), bat (for windows), cfg (salome context file) or all."), [])
parser.add_option('p', 'products', 'list2', 'products',
    _("Optional: Includes only the specified products."))
parser.add_option('', 'prefix', 'string', 'prefix',
    _("Optional: Specifies the prefix for the environment files."), "env")
parser.add_option('t', 'target', 'string', 'out_dir',
    _("Optional: Specifies the directory path where to put the environment "
      "files."),
    None)

# list of available shells with extensions
C_SHELLS = { "bash": "sh", "bat": "bat", "cfg" : "cfg", "tcl" : ""}
C_ALL_SHELL = [ "bash", "bat", "cfg", "tcl" ]


##
# Writes all the environment files
def write_all_source_files(config,
                           logger,
                           out_dir=None,
                           src_root=None,
                           silent=False,
                           shells=["bash"],
                           prefix="env",
                           env_info=None):
    '''Generates the environment files.
    
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param out_dir str: The path to the directory where the files will be put
    :param src_root str: The path to the directory where the sources are
    :param silent boolean: If True, do not print anything in the terminal
    :param shells list: The list of shells to generate
    :param prefix str: The prefix to add to the file names.
    :param env_info str: The list of products to add in the files.
    :return: The list of the generated files.
    :rtype: List
    '''
        
    if not out_dir:
        out_dir = config.APPLICATION.workdir

    if not os.path.exists(out_dir):
        raise src.SatException(_("Target directory not found: %s") % out_dir)

    if not silent:
        logger.write(_("Creating environment files for %s\n") % 
                     src.printcolors.printcLabel(config.APPLICATION.name), 2)
        src.printcolors.print_value(logger,
                                    _("Target"),
                                    src.printcolors.printcInfo(out_dir), 3)
        logger.write("\n", 3, False)
    
    shells_list = []
    all_shells = C_ALL_SHELL
    if "all" in shells:
        shells = all_shells
    else:
        shells = filter(lambda l: l in all_shells, shells)

    for shell in shells:
        if shell not in C_SHELLS:
            logger.write(_("Unknown shell: %s\n") % shell, 2)
        else:
            shells_list.append(src.environment.Shell(shell, C_SHELLS[shell]))
    
    writer = src.environment.FileEnvWriter(config,
                                           logger,
                                           out_dir,
                                           src_root,
                                           env_info)
    writer.silent = silent
    files = []
    for_build = True
    for_launch = False
    for shell in shells_list:
        if shell.name=="tcl":
            files.append(writer.write_tcl_files(for_launch,
                                                shell.name))
        else:
            files.append(writer.write_env_file("%s_launch.%s" %
                                               (prefix, shell.extension),
                                               for_launch,
                                               shell.name))
            files.append(writer.write_env_file("%s_build.%s" %
                                               (prefix, shell.extension),
                                               for_build,
                                               shell.name))

    for f in files:
        if f:
            logger.write("    "+f+"\n", 3)
    return files

##################################################

##
# Describes the command
def description():
    return _("The environ command generates the environment files of your "
             "application.\n\nexample:\nsat environ SALOME-master")

##
# Runs the command.
def run(args, runner, logger):
    (options, args) = parser.parse_args(args)

    # check that the command was called with an application
    src.check_config_has_application( runner.cfg )
    
    if options.products is None:
        environ_info = None
    else:
        # add products specified by user (only products 
        # included in the application)
        environ_info = filter(lambda l:
                              l in runner.cfg.APPLICATION.products.keys(),
                              options.products)
    
    if options.shell == []:
        shell = ["bash"]
        if src.architecture.is_windows():
            shell = ["bat"]
    else:
        shell = options.shell
    
    out_dir = options.out_dir
    if out_dir:
        out_dir = os.path.abspath(out_dir)
    
    write_all_source_files(runner.cfg, logger, out_dir=out_dir, shells=shell,
                           prefix=options.prefix, env_info=environ_info)
    logger.write("\n", 3, False)
