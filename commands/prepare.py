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

# Define all possible option for prepare command :  sat prepare <options>
parser = src.options.Options()
parser.add_option('p', 'product', 'list2', 'products',
    _('products to prepare. This option can be'
    ' passed several time to prepare several products.'))
parser.add_option('f', 'force', 'boolean', 'force', 
    _("force to prepare the products in development mode."))
parser.add_option('f', 'force_patch', 'boolean', 'force_patch', 
    _("force to apply patch to the products in development mode."))

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

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the prepare command description.
    :rtype: str
    '''
    return _("The prepare command gets the sources of "
             "the application products and apply the patches if there is any.")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with prepare parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    products_infos = get_products_list(options, runner.cfg, logger)

    ##################################
    ## Source command

    # Construct the option to pass to the source command
    args_appli = runner.cfg.VARS.application + ' '

    args_product_opt = '--product '
    if options.products:
        for p_name in options.products:
            args_product_opt += ',' + p_name
    else:
        for p_name, __ in products_infos:
            args_product_opt += ',' + p_name
      
    args_source = args_appli + args_product_opt
        
    if options.force:
        args_source += ' --force'
    
    # Call the source command that gets the source
    msg = src.printcolors.printcHeader(
                                _('Get the sources of the desired products\n'))
    logger.write(msg)
    res_source = runner.source(args_source)
    
    
    ##################################
    ## Patch command
    msg = src.printcolors.printcHeader(
                    _('\nApply the patches to the sources of the products\n'))
    logger.write(msg)

    # Construct the option to pass to the patch command
    ldev_products = [p for p in products_infos if src.product.product_is_dev(p[1])]
    if len(ldev_products) > 0 and not options.force_patch:
        msg = _("Ignoring the following products "
                "in development mode\n")
        logger.write(src.printcolors.printcWarning(msg), 1)
        for i, (product_name, __) in enumerate(ldev_products):
            args_product_opt = args_product_opt.replace(',' + product_name, '')
            end_text = ', '
            if i+1 == len(ldev_products):
                end_text = '\n'
                
            logger.write(product_name + end_text, 1)
        
        msg = _("Use the --force_patch option to apply the patches anyway\n\n")
        logger.write(src.printcolors.printcWarning(msg), 1)
            
    if args_product_opt == '--product ':
        msg = _("Nothing to patch\n")
        logger.write(msg)
        res_patch = 0
    else:
        args_patch = args_appli + args_product_opt
        
        # Call the source command that gets the source
        res_patch = runner.patch(args_patch)
    
    return res_source + res_patch