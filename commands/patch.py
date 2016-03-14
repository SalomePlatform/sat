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
import prepare

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('p', 'product', 'list2', 'products',
    _('products to get the sources. This option can be'
    ' passed several time to get the sources of several products.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not get sources from sample products."))

def apply_patch(config, product_info, logger):
    '''The method called to apply patches on a product

    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product to be patched
    :param logger Logger: The logger instance to use for the display and logging
    :return: (True if it succeed, else False, message to display)
    :rtype: (boolean, str)
    '''
    
    if not "patches" in product_info or len(product_info.patches) == 0:
        msg = _("No patch for the %s product") % product_info.name
        logger.write(msg, 3)
        logger.write("\n", 1)
        return True, ""

    if not os.path.exists(product_info.source_dir):
        msg = _("No sources found for the %s product\n") % product_info.name
        logger.write(src.printcolors.printcWarning(msg), 1)
        return False, ""

    # At this point, there one or more patches and the source directory exists
    retcode = []
    res = []
    # Loop on all the patches of the product
    for patch in product_info.patches:
        details = []
        
        # Check the existence and apply the patch
        if os.path.isfile(patch):
            #patch_exe = "patch" # old patch command (now replace by patch.py)
            patch_exe = os.path.join(config.VARS.srcDir, "patching.py")
            patch_cmd = "python %s -p1 -- < %s" % (patch_exe, patch)

            logger.write(("    >%s\n" % patch_cmd),5)
            res_cmd = (subprocess.call(patch_cmd, 
                                   shell=True, 
                                   cwd=product_info.source_dir,
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
            retcode.append("%s: %s" % (product_info.name, message))
        
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
             "the application products if there is any")
  
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

    # Get the products list with products informations reagrding the options
    products_infos = prepare.get_products_list(options, runner.cfg, logger)
    
    # Get the maximum name length in order to format the terminal display
    max_product_name_len = 1
    if len(products_infos) > 0:
        max_product_name_len = max(map(lambda l: len(l), products_infos[0])) + 4
    
    # The loop on all the products on which to apply the patches
    good_result = 0
    for product_name, product_info in products_infos:
        # display and log
        logger.write('%s: ' % src.printcolors.printcLabel(product_name), 3)
        logger.write(' ' * (max_product_name_len - len(product_name)), 3, False)
        logger.write("\n", 4, False)
        return_code, patch_res = apply_patch(runner.cfg, product_info, logger)
        logger.write(patch_res, 1, False)
        if return_code:
            good_result += 1
    
    # Display the results (how much passed, how much failed, etc...)

    logger.write("\n", 2, False)
    if good_result == len(products_infos):
        status = src.OK_STATUS
        res_count = "%d / %d" % (good_result, good_result)
    else:
        status = src.KO_STATUS
        res_count = "%d / %d" % (good_result, len(products_infos))
    
    # write results
    logger.write("Patching sources of the application:", 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)
    
    return len(products_infos) - good_result