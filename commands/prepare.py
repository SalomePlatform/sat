#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2012  CEA/DEN
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

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('m', 'module', 'list2', 'modules',
    _('modules to prepare. This option can be'
    ' passed several time to prepare several modules.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not prepare sample modules."))
parser.add_option('f', 'force', 'boolean', 'force', 
    _("force to prepare the modules in development mode."))

def get_modules_list(options, cfg, logger):
    '''method that gives the module list with their informations from 
       configuration regarding the passed options.
    
    :param options Options: The Options instance that stores the commands 
                            arguments
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display and logging
    :return: The list of (module name, module_infomrmations).
    :rtype: List
    '''
    # Get the modules to be prepared, regarding the options
    if options.modules is None:
        # No options, get all modules sources
        modules = cfg.APPLICATION.modules
    else:
        # if option --modules, check that all modules of the command line
        # are present in the application.
        modules = options.modules
        for m in modules:
            if m not in cfg.APPLICATION.modules:
                raise src.SatException(_("Module %(module)s "
                            "not defined in application %(application)s") %
                { 'module': m, 'application': cfg.VARS.application} )
    
    # Construct the list of tuple containing 
    # the modules name and their definition
    modules_infos = src.module.get_modules_infos(modules, cfg)

    # if the --no_sample option is invoked, suppress the sample modules from 
    # the list
    if options.no_sample:
        
        lmodules_sample = [m for m in modules_infos if src.module.module_is_sample(m[1])]
        
        modules_infos = [m for m in modules_infos if m not in lmodules_sample]

        if len(lmodules_sample) > 0:
            logger.write(src.printcolors.printcWarning(_("Ignoring the following sample modules:\n")), 1)
        for i, module in enumerate(lmodules_sample):
            end_text = ', '
            if i+1 == len(lmodules_sample):
                end_text = '\n'
                
            logger.write(module[0] + end_text, 1)
    
    return modules_infos

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the prepare command description.
    :rtype: str
    '''
    return _("The prepare command apply the patches on the sources of "
             "the application modules if there is any")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with prepare parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Construct the option to pass to the source command
    args_source = runner.cfg.VARS.application + ' '
    
    if options.modules:
        args_source += '--module ' + ','.join(options.modules)
    
    if options.no_sample:
        args_source += ' --no_sample'
        
    if options.force:
        args_source += ' --force'
    
    # Call the source command that gets the source
    msg = src.printcolors.printcHeader(
                                _('Get the sources of the desired modules\n'))
    logger.write(msg)
    res_source = runner.source(args_source)
    
    # Construct the option to pass to the patch command
    args_patch = args_source.replace(' --force', '')
    
    # Call the source command that gets the source
    msg = src.printcolors.printcHeader(
                    _('\nApply the patches to the sources of the modules\n'))
    logger.write(msg)
    res_patch = runner.patch(args_patch)
    
    return res_source + res_patch