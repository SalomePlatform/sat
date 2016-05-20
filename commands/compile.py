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

import src

# Define all possible option for the compile command :  sat compile <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('products to configure. This option can be'
    ' passed several time to configure several products.'))
parser.add_option('', 'with_fathers', 'boolean', 'fathers',
    _("build all necessary modules to the given module (KERNEL is build before"
      " building GUI)."), False)
parser.add_option('', 'with_children', 'boolean', 'children',
    _("build all modules using the given module (all SMESH plugins are build "
      "after SMESH)."), False)
parser.add_option('', 'clean_all', 'boolean', 'clean_all',
    _("clean BUILD dir and INSTALL dir before building module."), False)
parser.add_option('', 'clean_install', 'boolean', 'clean_install',
    _("clean INSTALL dir before building module."), False)
parser.add_option('', 'make_flags', 'string', 'makeflags',
    _("add extra options to the 'make' command."))
parser.add_option('', 'show', 'boolean', 'no_compile',
    _("DO NOT COMPILE just show if modules are installed or not."), False)
parser.add_option('', 'stop_first_fail', 'boolean', 'stop_first_fail', _("Stop"
                    "s the command at first module compilation fail."), False)

def get_products_list(options, cfg, logger):
    '''method that gives the product list with their informations from 
       configuration regarding the passed options.
    
    :param options Options: The Options instance that stores the commands 
                            arguments
    :param cfg Config: The global configuration
    :param logger Logger: The logger instance to use for the display and 
                          logging
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
    
    products_infos = [pi for pi in products_infos if not(
                                     src.product.product_is_native(pi[1]) or 
                                     src.product.product_is_fixed(pi[1]))]
    
    return products_infos

def get_recursive_fathers(config, p_name_p_info, without_native_fixed=False):
    """ Get the recursive list of the dependencies of the product defined by
        prod_info
    
    :param config Config: The global configuration
    :param prod_info Config: The specific config of the product
    :param without_native_fixed boolean: If true, do not include the fixed
                                         or native products in the result
    :return: The list of product_informations.
    :rtype: List
    """
    p_name, p_info = p_name_p_info
    # Initialization of the resulting list
    l_fathers = []
    # Minimal case : no dependencies
    if "depend" not in p_info or p_info.depend == []:
        return []
    # Add the dependencies and call the function to get the dependencies of the
    # dependencies
    for father_name in p_info.depend:
        l_fathers_name = [pn_pi[0] for pn_pi in l_fathers]
        if father_name not in l_fathers_name:
            if father_name not in config.APPLICATION.products:
                msg = _("The product %(father_name)s that is in %(product_nam"
                        "e)s dependencies is not present in application "
                        "%(appli_name)s" % {"father_name" : father_name, 
                                    "product_name" : p_name.name, 
                                    "appli_name" : config.VARS.application})
                raise src.SatException(msg)
            prod_info_father = src.product.get_product_config(config,
                                                              father_name)
            pname_pinfo_father = (prod_info_father.name, prod_info_father)
            # Do not append the father if the it is native or fixed and 
            # the corresponding parameter is called
            if without_native_fixed:
                if not(src.product.product_is_native(prod_info_father) or 
                       src.product.product_is_fixed(prod_info_father)):
                    l_fathers.append(pname_pinfo_father)
            else:
                l_fathers.append(pname_pinfo_father)
            # Get the dependencies of the dependency
            l_grand_fathers = get_recursive_fathers(config,
                                pname_pinfo_father,
                                without_native_fixed = without_native_fixed)
            l_fathers += l_grand_fathers
    return l_fathers

def sort_products(config, p_infos):
    """ Sort the p_infos regarding the dependencies between the products
    
    :param config Config: The global configuration
    :param p_infos list: List of (str, Config) => (product_name, product_info)
    """
    l_prod_sorted = deepcopy_list(p_infos)
    for prod in p_infos:
        l_fathers = get_recursive_fathers(config, prod, without_native_fixed=True)
        l_fathers = [father for father in l_fathers if father in p_infos]
        if l_fathers == []:
            continue
        for p_sorted in l_prod_sorted:
            if p_sorted in l_fathers:
                l_fathers.remove(p_sorted)
            if l_fathers==[]:
                l_prod_sorted.remove(prod)
                l_prod_sorted.insert(l_prod_sorted.index(p_sorted)+1, prod)
                break
        
    return l_prod_sorted
       
def deepcopy_list(input_list):
    res = []
    for elem in input_list:
        res.append(elem)
    return res

def log_step(logger, header, step):
    logger.write("\r%s%s" % (header, " " * 20), 3)
    logger.write("\r%s%s" % (header, step), 3)
    logger.write("\n==== %s \n" % src.printcolors.printcInfo(step), 4)
    logger.flush()

def log_res_step(logger, res):
    if res == 0:
        logger.write("%s \n" % src.printcolors.printcSuccess("OK"), 4)
        logger.flush()
    else:
        logger.write("%s \n" % src.printcolors.printcError("KO"), 4)
        logger.flush()

def compile_all_products(sat, config, products_infos, logger):
    '''Execute the proper configuration commands 
       in each product build directory.

    :param config Config: The global configuration
    :param products_info list: List of 
                                 (str, Config) => (product_name, product_info)
    :param logger Logger: The logger instance to use for the display and logging
    :return: the number of failing commands.
    :rtype: int
    '''
    res = 0
    for p_name_info in products_infos:
        res_prod = compile_product(sat, p_name_info, config, logger)
        if res_prod != 0:
            res += 1 
    return res

def compile_product(sat, p_name_info, config, logger):
    '''Execute the proper configuration command(s) 
       in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :return: 1 if it fails, else 0.
    :rtype: int
    '''
    
    p_name, __ = p_name_info
    
    # Logging
    logger.write("\n", 4, False)
    logger.write("################ ", 4)
    header = _("Compilation of %s") % src.printcolors.printcLabel(p_name)
    header += " %s " % ("." * (20 - len(p_name)))
    logger.write(header, 3)
    logger.write("\n", 4, False)
    logger.flush()
    
    # Execute "sat configure", "sat make" and "sat install"
    len_end_line = 20
    res = 0

    log_step(logger, header, "CONFIGURE")
    res_c = sat.configure(config.VARS.application + " --products " + p_name, verbose = 0)
    log_res_step(logger, res_c)
    res += res_c
    
    log_step(logger, header, "MAKE")
    res_c = sat.make(config.VARS.application + " --products " + p_name, verbose = 0)
    log_res_step(logger, res_c)
    res += res_c

    log_step(logger, header, "MAKE INSTALL")
    res_c = sat.makeinstall(config.VARS.application + " --products " + p_name, verbose = 0)
    log_res_step(logger, res_c)
    res += res_c
    
    # Log the result
    if res > 0:
        logger.write("\r%s%s" % (header, " " * len_end_line), 3)
        logger.write("\r" + header + src.printcolors.printcError("KO"))
        logger.write("==== %(KO)s in compile of %(name)s \n" %
            { "name" : p_name , "KO" : src.printcolors.printcInfo("ERROR")}, 4)
        logger.flush()
    else:
        logger.write("\r%s%s" % (header, " " * len_end_line), 3)
        logger.write("\r" + header + src.printcolors.printcSuccess("OK"))
        logger.write("==== %s \n" % src.printcolors.printcInfo("OK"), 4)
        logger.write("==== Make of %(name)s %(OK)s \n" %
            { "name" : p_name , "OK" : src.printcolors.printcInfo("OK")}, 4)
        logger.flush()
    logger.write("\n", 3, False)

    return res

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the compile command description.
    :rtype: str
    '''
    return _("The compile command construct the products of the application")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with compile parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Get the list of products to treat
    products_infos = get_products_list(options, runner.cfg, logger)

    # Sort the list regarding the dependencies of the products
    products_infos = sort_products(runner.cfg, products_infos)

    # Print some informations
    logger.write(_('Executing the compile command in the build '
                                'directories of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    
    info = [
            (_("SOURCE directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'SOURCES')),
            (_("BUILD directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'BUILD'))
            ]
    src.print_info(logger, info)
    
    # Call the function that will loop over all the products and execute
    # the right command(s)
    res = compile_all_products(runner, runner.cfg, products_infos, logger)
    
    # Print the final state
    nb_products = len(products_infos)
    if res == 0:
        final_status = "OK"
    else:
        final_status = "KO"
   
    logger.write(_("\nCompilation: %(status)s (%(valid_result)d/%(nb_products)d)\n") % \
        { 'status': src.printcolors.printc(final_status), 
          'valid_result': nb_products - res,
          'nb_products': nb_products }, 1)    
    
    return res 