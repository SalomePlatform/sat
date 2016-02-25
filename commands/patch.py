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

import os
import subprocess

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('m', 'module', 'list2', 'modules',
    _('modules to get the sources. This option can be'
    ' passed several time to get the sources of several modules.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not get sources from sample modules."))

def apply_patch(config, module_info, logger):
    if not "patches" in module_info or len(module_info.patches) == 0:
        msg = _("No patch for the %s module") % module_info.name
        logger.write(msg, 3)
        logger.write("\n", 1)
        return True, ""

    if not os.path.exists(module_info.source_dir):
        msg = _("No sources found for the %s module\n") % module_info.name
        logger.write(src.printcolors.printcWarning(msg), 1)
        return False, ""

    retcode = []
    res = []
    for patch in module_info.patches:
        details = []

        if os.path.isfile(patch) and patch.endswith(".patch"):
            #patch_exe = "patch" # old patch command (now replace by patch.py)
            patch_exe = os.path.join(config.VARS.srcDir, "patching.py")
            patch_cmd = "python %s -p1 -- < %s" % (patch_exe, patch)

            logger.write(("    >%s\n" % patch_cmd),5)
            res_cmd = (subprocess.call(patch_cmd, 
                                   shell=True, 
                                   cwd=module_info.source_dir,
                                   stdout=logger.logTxtFile, 
                                   stderr=subprocess.STDOUT) == 0)        
        else:
            res_cmd = False
            details.append("  " + 
                src.printcolors.printcError(_("Not a valid patch: %s") % patch))

        res.append(res_cmd)
        
        if res_cmd:
            message = (_("Apply patch %s") % 
                       src.printcolors.printcHighlight(patch))
        else:
            message = src.printcolors.printcWarning(
                                        _("Failed to apply patch %s") % patch)

        if config.USER.output_level >= 3:
            retcode.append("  %s" % message)
        else:
            retcode.append("%s: %s" % (module_info.name, message))
        
        if len(details) > 0:
            retcode.extend(details)

    res = not (False in res)
    
    return res, "\n".join(retcode) + "\n"

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the patch command description.
    :rtype: str
    '''
    return _("The patch command apply the patches on the sources of "
             "the application modules if there is any")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with patch parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Print some informations
    logger.write('Patching sources of the application %s\n' % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)

    src.printcolors.print_value(logger, 'out_dir', 
                                runner.cfg.APPLICATION.out_dir, 2)
    logger.write("\n", 2, False)

    # Get the modules to be prepared, regarding the options
    if options.modules is None:
        # No options, get all modules sources
        modules = runner.cfg.APPLICATION.modules
    else:
        # if option --modules, check that all modules of the command line
        # are present in the application.
        modules = options.modules
        for m in modules:
            if m not in runner.cfg.APPLICATION.modules:
                raise src.SatException(_("Module %(module)s "
                            "not defined in appplication %(application)s") %
                { 'module': m, 'application': runner.cfg.VARS.application} )
    
    # Construct the list of tuple containing 
    # the modules name and their definition
    modules_infos = src.module.get_modules_infos(modules, runner.cfg)

    # if the --no_sample option is invoked, suppress the sample modules from 
    # the list
    if options.no_sample:
        modules_infos = filter(lambda l: not src.module.module_is_sample(l[1]),
                         modules_infos)
    
    # Get the maximum name length in order to format the terminal display
    max_module_name_len = 1
    if len(modules_infos) > 0:
        max_module_name_len = max(map(lambda l: len(l), modules_infos[0])) + 4
    
    # The loop on all the modules on which to apply the patches
    good_result = 0
    for module_name, module_info in modules_infos:
        # display and log
        logger.write('%s: ' % src.printcolors.printcLabel(module_name), 3)
        logger.write(' ' * (max_module_name_len - len(module_name)), 3, False)
        logger.write("\n", 4, False)
        return_code, patch_res = apply_patch(runner.cfg, module_info, logger)
        logger.write(patch_res, 1, False)
        if return_code:
            good_result += 1
    
    # Display the results (how much passed, how much failed, etc...)

    logger.write("\n", 2, False)
    if good_result == len(modules_infos):
        status = src.OK_STATUS
        res_count = "%d / %d" % (good_result, good_result)
    else:
        status = src.KO_STATUS
        res_count = "%d / %d" % (good_result, len(modules))
    
    # write results
    logger.write("Patching sources of the application:", 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)
    
    return len(modules_infos) - good_result