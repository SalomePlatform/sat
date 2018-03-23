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

import src
import src.debug as DBG

# Define all possible option for prepare command :  sat prepare <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to prepare. This option can be'
    ' passed several time to prepare several products.'))
parser.add_option('f', 'force', 'boolean', 'force', 
    _("Optional: force to prepare the products in development mode."))
parser.add_option('', 'force_patch', 'boolean', 'force_patch', 
    _("Optional: force to apply patch to the products in development mode."))

def get_products_list(options, cfg, logger):
    '''method that gives the product list with their informations from 
       configuration regarding the passed options.
    
    :param options Options: The Options instance that stores the commands 
                            arguments
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display and logging
    :return: The list of (product name, product_informations).
    :rtype: List
    '''
    # Get the products to be prepared, regarding the options
    if options.products is None:
        # No options, get all products sources
        products = cfg.APPLICATION.products
    else:
        # if option --products, check that all products of the command line
        # are present in the application.
        products = options.products
        for p in products:
            if p not in cfg.APPLICATION.products:
                raise src.SatException(_("Product %(product)s "
                            "not defined in application %(application)s") %
                        { 'product': p, 'application': cfg.VARS.application} )
    
    # Construct the list of tuple containing 
    # the products name and their definition
    products_infos = src.product.get_products_infos(products, cfg)
    
    return products_infos

def remove_products(arguments, l_products_info, logger):
    '''function that removes the products in l_products_info from arguments list.
    
    :param arguments str: The arguments from which to remove products
    :param l_products_info list: List of 
                                 (str, Config) => (product_name, product_info)
    :param logger Logger: The logger instance to use for the display and logging
    :return: The updated arguments.
    :rtype: str
    '''
    args = str(arguments) #copy of "--products ,XDATA,TESSCODE,cmake" for example
    largs = args.split(',')
    DBG.write("largs", largs)
    toRemove = [name for name, xx in l_products_info]
    DBG.write("remove_products", toRemove)
    removed = []
    notRemoved = []
    for name in largs[1:]: # skip largs[0] as "--products "
      if name in toRemove:
        removed.append(name)
      else:
        notRemoved.append(name)
    # DBG.write(removed, removed, True)
    logger.write("  %s\n" % ",".join(removed), 1)
    DBG.write("notRemoved", notRemoved)
    res = largs[0] + ",".join(notRemoved)
    return res

def find_products_already_getted(l_products):
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
        if os.path.exists(prod_cfg.source_dir):
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

    products_infos = get_products_list(options, runner.cfg, logger)

    # Construct the arguments to pass to the clean, source and patch commands
    args_appli = runner.cfg.VARS.application + ' '
    args_product_opt = '--products '
    if options.products:
        for p_name in options.products:
            args_product_opt += ',' + p_name
    else:
        for p_name, __ in products_infos:
            args_product_opt += ',' + p_name

    ldev_products = [p for p in products_infos if src.product.product_is_dev(p[1])]
    args_product_opt_clean = args_product_opt
    if not options.force and len(ldev_products) > 0:
        l_products_not_getted = find_products_already_getted(ldev_products)
        if len(l_products_not_getted) > 0:
            msg = _("""\
Do not get the source of the following products in development mode
Use the --force option to overwrite it.
""")
            logger.write(src.printcolors.printcWarning(msg), 1)
            args_product_opt_clean = remove_products(args_product_opt_clean,
                                                     l_products_not_getted,
                                                     logger)
            logger.write("\n", 1)

    
    args_product_opt_patch = args_product_opt
    if not options.force_patch and len(ldev_products) > 0:
        l_products_with_patchs = find_products_with_patchs(ldev_products)
        if len(l_products_with_patchs) > 0:
            msg = _("""\
do not patch the following products in development mode
Use the --force_patch option to overwrite it.
""")
            logger.write(src.printcolors.printcWarning(msg), 1)
            args_product_opt_patch = remove_products(args_product_opt_patch,
                                                     l_products_with_patchs,
                                                     logger)
            logger.write("\n", 1)

    # Construct the final commands arguments
    args_clean = args_appli + args_product_opt_clean + " --sources"
    args_source = args_appli + args_product_opt  
    args_patch = args_appli + args_product_opt_patch

    # If there is no more any product in the command arguments,
    # do not call the concerned command 
    oExpr = re.compile("^--products *$")
    do_clean = not(oExpr.search(args_product_opt_clean))
    do_source = not(oExpr.search(args_product_opt))
    do_patch = not(oExpr.search(args_product_opt_patch))
    
    
    # Initialize the results to a failing status
    res_clean = 1
    res_source = 1
    res_patch = 1
    
    # Call the commands using the API
    if do_clean:
        msg = _("Clean the source directories ...")
        logger.write(msg, 3)
        logger.flush()
        res_clean = runner.clean(args_clean, batch=True, verbose = 0,
                                    logger_add_link = logger)
        if res_clean == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 3)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 3)
    if do_source:
        msg = _("Get the sources of the products ...")
        logger.write(msg, 5)
        res_source = runner.source(args_source,
                                    logger_add_link = logger)
        if res_source == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 5)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 5)
    if do_patch:
        msg = _("Patch the product sources (if any) ...")
        logger.write(msg, 5)
        res_patch = runner.patch(args_patch,
                                    logger_add_link = logger)
        if res_patch == 0:
            logger.write('%s\n' % src.printcolors.printc(src.OK_STATUS), 5)
        else:
            logger.write('%s\n' % src.printcolors.printc(src.KO_STATUS), 5)
    
    return res_clean + res_source + res_patch
