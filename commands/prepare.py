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

import re
import os
import pprint as PP

import src
import src.debug as DBG


# Define all possible option for prepare command :  sat prepare <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to prepare. This option accepts a comma separated list.'))
parser.add_option('f', 'force', 'boolean', 'force',
    _("Optional: force to prepare the products in development mode."))
parser.add_option('', 'force_patch', 'boolean', 'force_patch', 
    _("Optional: force to apply patch to the products in development mode."))
parser.add_option('c', 'complete', 'boolean', 'complete',
    _("Optional: completion mode, only prepare products not present in SOURCES dir."),
    False)


def find_products_already_prepared(l_products):
    '''function that returns the list of products that have an existing source 
       directory.
    
    :param l_products List: The list of products to check
    :return: The list of product configurations that have an existing source 
             directory.
    :rtype: List
    '''
    l_res = []
    for p_name_p_cfg in l_products:
        __, prod_cfg = p_name_p_cfg
        if "source_dir" in prod_cfg and os.path.exists(prod_cfg.source_dir):
            l_res.append(p_name_p_cfg)
    return l_res

def find_products_with_patchs(l_products):
    '''function that returns the list of products that have one or more patches.
    
    :param l_products List: The list of products to check
    :return: The list of product configurations that have one or more patches.
    :rtype: List
    '''
    l_res = []
    for p_name_p_cfg in l_products:
        __, prod_cfg = p_name_p_cfg
        l_patchs = src.get_cfg_param(prod_cfg, "patches", [])
        if len(l_patchs)>0:
            l_res.append(p_name_p_cfg)
    return l_res

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the prepare command description.
    :rtype: str
    '''
    return _("The prepare command gets the sources of "
             "the application products and apply the patches if there is any."
             "\n\nexample:\nsat prepare SALOME-master --products KERNEL,GUI")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with prepare parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # write warning if platform is not declared as supported
    src.check_platform_is_supported( runner.cfg, logger )

    products_infos = src.product.get_products_list(options, runner.cfg, logger)

    # Construct the arguments to pass to the clean, source and patch commands
    args_appli = runner.cfg.VARS.application + " "  # useful whitespace
    if options.products:
        listProd = list(options.products)
    else: # no product interpeted as all products
        listProd = [name for name, tmp in products_infos]

    if options.complete:
        # remove products that are already prepared 'completion mode)
        pi_already_prepared=find_products_already_prepared(products_infos)
        l_already_prepared = [i for i, tmp in pi_already_prepared]
        newList, removedList = removeInList(listProd, l_already_prepared)
        listProd = newList
        if len(newList) == 0 and len(removedList) > 0 :
            msg = "\nAll the products are already installed, do nothing!\n"
            logger.write(src.printcolors.printcWarning(msg), 1)
            return 0
        if len(removedList) > 0 :
            msg = "\nList of already prepared products that are skipped : %s\n" % ",".join(removedList)
            logger.write(msg, 3)
        

    args_product_opt = '--products ' + ",".join(listProd)
    do_source = (len(listProd) > 0)


    ldev_products = [p for p in products_infos if src.product.product_is_dev(p[1])]
    newList = listProd # default
    if not options.force and len(ldev_products) > 0:
        l_products_not_getted = find_products_already_prepared(ldev_products)
        listNot = [i for i, tmp in l_products_not_getted]
        newList, removedList = removeInList(listProd, listNot)
        if len(removedList) > 0:
            msg = _("""\
Do not get the source of the following products in development mode.
Use the --force option to overwrite it.
""")
            msg += "\n%s\n" % ",".join(removedList)
            logger.write(src.printcolors.printcWarning(msg), 1)

    args_product_opt_clean = '--products ' + ",".join(newList)
    do_clean = (len(newList) > 0)
    
    newList = listProd # default
    if not options.force_patch and len(ldev_products) > 0:
        l_products_with_patchs = find_products_with_patchs(ldev_products)
        listNot = [i for i, tmp in l_products_with_patchs]
        newList, removedList = removeInList(listProd, listNot)
        if len(removedList) > 0:
            msg = _("""\
Do not patch the following products in development mode.
Use the --force_patch option to overwrite it.
""")
            msg += "\n%s\n" % ",".join(removedList)
            logger.write(src.printcolors.printcWarning(msg), 1)
                                                     
    args_product_opt_patch = '--products ' + ",".join(newList)
    do_patch = (len(newList) > 0)
      
    # Construct the final commands arguments
    args_clean = args_appli + args_product_opt_clean + " --sources"
    args_source = args_appli + args_product_opt  
    args_patch = args_appli + args_product_opt_patch
      
    # Initialize the results to a running status
    res_clean = 0
    res_source = 0
    res_patch = 0
    
    # Call the commands using the API
    if do_clean:
        msg = _("Clean the source directories ...")
        logger.write(msg, 3)
        logger.flush()
        res_clean = runner.clean(args_clean, batch=True, verbose = 0, logger_add_link = logger)
        if res_clean == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 3)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 3)
    if do_source:
        msg = _("Get the sources of the products ...")
        logger.write(msg, 5)
        res_source = runner.source(args_source, logger_add_link = logger)
        if res_source == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 5)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 5)
    if do_patch:
        msg = _("Patch the product sources (if any) ...")
        logger.write(msg, 5)
        res_patch = runner.patch(args_patch, logger_add_link = logger)
        if res_patch == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 5)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 5)
    
    return res_clean + res_source + res_patch


def removeInList(aList, removeList):
    """Removes elements of removeList list from aList
    
    :param aList: (list) The list from which to remove elements
    :param removeList: (list) The list which contains elements to remove
    :return: (list, list) (list with elements removed, list of elements removed) 
    """
    res1 = [i for i in aList if i not in removeList]
    res2 = [i for i in aList if i in removeList]
    return (res1, res2)


