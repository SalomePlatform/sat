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

# Compatibility python 2/3 for input function
# input stays input for python 3 and input = raw_input for python 2
try: 
    input = raw_input
except NameError: 
    pass

# Define all possible option for the compile command :  sat compile <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to configure. This option can be'
    ' passed several time to configure several products.'))
parser.add_option('', 'with_fathers', 'boolean', 'fathers',
    _("Optional: build all necessary products to the given product (KERNEL is "
      "build before building GUI)."), False)
parser.add_option('', 'with_children', 'boolean', 'children',
    _("Optional: build all products using the given product (all SMESH plugins"
      " are build after SMESH)."), False)
parser.add_option('', 'clean_all', 'boolean', 'clean_all',
    _("Optional: clean BUILD dir and INSTALL dir before building product."),
    False)
parser.add_option('', 'clean_install', 'boolean', 'clean_install',
    _("Optional: clean INSTALL dir before building product."), False)
parser.add_option('', 'make_flags', 'string', 'makeflags',
    _("Optional: add extra options to the 'make' command."))
parser.add_option('', 'show', 'boolean', 'no_compile',
    _("Optional: DO NOT COMPILE just show if products are installed or not."),
    False)
parser.add_option('', 'stop_first_fail', 'boolean', 'stop_first_fail', _(
                  "Optional: Stops the command at first product compilation"
                  " fail."), False)

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
                                     src.product.product_is_fixed(pi[1]))]
    
    return products_infos

def get_children(config, p_name_p_info):
    l_res = []
    p_name, __ = p_name_p_info
    # Get all products of the application
    products = config.APPLICATION.products
    products_infos = src.product.get_products_infos(products, config)
    for p_name_potential_child, p_info_potential_child in products_infos:
        if ("depend" in p_info_potential_child and 
                p_name in p_info_potential_child.depend):
            l_res.append(p_name_potential_child)
    return l_res

def get_recursive_children(config, p_name_p_info, without_native_fixed=False):
    """ Get the recursive list of the product that depend on 
        the product defined by prod_info
    
    :param config Config: The global configuration
    :param prod_info Config: The specific config of the product
    :param without_native_fixed boolean: If true, do not include the fixed
                                         or native products in the result
    :return: The list of product_informations.
    :rtype: List
    """
    p_name, __ = p_name_p_info
    # Initialization of the resulting list
    l_children = []
    
    # Get the direct children (not recursive)
    l_direct_children = get_children(config, p_name_p_info)
    # Minimal case : no child
    if l_direct_children == []:
        return []
    # Add the children and call the function to get the children of the
    # children
    for child_name in l_direct_children:
        l_children_name = [pn_pi[0] for pn_pi in l_children]
        if child_name not in l_children_name:
            if child_name not in config.APPLICATION.products:
                msg = _("The product %(child_name)s that is in %(product_nam"
                        "e)s children is not present in application "
                        "%(appli_name)s" % {"child_name" : child_name, 
                                    "product_name" : p_name.name, 
                                    "appli_name" : config.VARS.application})
                raise src.SatException(msg)
            prod_info_child = src.product.get_product_config(config,
                                                              child_name)
            pname_pinfo_child = (prod_info_child.name, prod_info_child)
            # Do not append the child if it is native or fixed and 
            # the corresponding parameter is called
            if without_native_fixed:
                if not(src.product.product_is_native(prod_info_child) or 
                       src.product.product_is_fixed(prod_info_child)):
                    l_children.append(pname_pinfo_child)
            else:
                l_children.append(pname_pinfo_child)
            # Get the children of the children
            l_grand_children = get_recursive_children(config,
                                pname_pinfo_child,
                                without_native_fixed = without_native_fixed)
            l_children += l_grand_children
    return l_children

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
                                    "product_name" : p_name, 
                                    "appli_name" : config.VARS.application})
                raise src.SatException(msg)
            prod_info_father = src.product.get_product_config(config,
                                                              father_name)
            pname_pinfo_father = (prod_info_father.name, prod_info_father)
            # Do not append the father if it is native or fixed and 
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
            for item in l_grand_fathers:
                if item not in l_fathers:
                    l_fathers.append(item)
    return l_fathers

def sort_products(config, p_infos):
    """ Sort the p_infos regarding the dependencies between the products
    
    :param config Config: The global configuration
    :param p_infos list: List of (str, Config) => (product_name, product_info)
    """
    l_prod_sorted = src.deepcopy_list(p_infos)
    for prod in p_infos:
        l_fathers = get_recursive_fathers(config,
                                          prod,
                                          without_native_fixed=True)
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

def extend_with_fathers(config, p_infos):
    p_infos_res = src.deepcopy_list(p_infos)
    for p_name_p_info in p_infos:
        fathers = get_recursive_fathers(config,
                                        p_name_p_info,
                                        without_native_fixed=True)
        for p_name_p_info_father in fathers:
            if p_name_p_info_father not in p_infos_res:
                p_infos_res.append(p_name_p_info_father)
    return p_infos_res

def extend_with_children(config, p_infos):
    p_infos_res = src.deepcopy_list(p_infos)
    for p_name_p_info in p_infos:
        children = get_recursive_children(config,
                                        p_name_p_info,
                                        without_native_fixed=True)
        for p_name_p_info_child in children:
            if p_name_p_info_child not in p_infos_res:
                p_infos_res.append(p_name_p_info_child)
    return p_infos_res    

def check_dependencies(config, p_name_p_info):
    l_depends_not_installed = []
    fathers = get_recursive_fathers(config, p_name_p_info, without_native_fixed=True)
    for p_name_father, p_info_father in fathers:
        if not(src.product.check_installation(p_info_father)):
            l_depends_not_installed.append(p_name_father)
    return l_depends_not_installed

def log_step(logger, header, step):
    logger.write("\r%s%s" % (header, " " * 30), 3)
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

def compile_all_products(sat, config, options, products_infos, logger):
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
        
        p_name, p_info = p_name_info
        
        # Logging
        len_end_line = 30
        logger.write("\n", 4, False)
        logger.write("################ ", 4)
        header = _("Compilation of %s") % src.printcolors.printcLabel(p_name)
        header += " %s " % ("." * (len_end_line - len(p_name)))
        logger.write(header, 3)
        logger.write("\n", 4, False)
        logger.flush()

        # Do nothing if the product is not compilable
        if ("properties" in p_info and "compilation" in p_info.properties and 
                                            p_info.properties.compilation == "no"):
            log_step(logger, header, "ignored")
            logger.write("\n", 3, False)
            continue

        # Do nothing if the product is native
        if src.product.product_is_native(p_info):
            log_step(logger, header, "native")
            logger.write("\n", 3, False)
            continue

        # Clean the build and the install directories 
        # if the corresponding options was called
        if options.clean_all:
            log_step(logger, header, "CLEAN BUILD AND INSTALL")
            sat.clean(config.VARS.application + 
                      " --products " + p_name + 
                      " --build --install",
                      batch=True,
                      verbose=0,
                      logger_add_link = logger)
        
        # Clean the the install directory 
        # if the corresponding option was called
        if options.clean_install and not options.clean_all:
            log_step(logger, header, "CLEAN INSTALL")
            sat.clean(config.VARS.application + 
                      " --products " + p_name + 
                      " --install",
                      batch=True,
                      verbose=0,
                      logger_add_link = logger)
        
        # Check if it was already successfully installed
        if src.product.check_installation(p_info):
            logger.write(_("Already installed\n"))
            continue
        
        # If the show option was called, do not launch the compilation
        if options.no_compile:
            logger.write(_("Not installed\n"))
            continue
        
        # Check if the dependencies are installed
        l_depends_not_installed = check_dependencies(config, p_name_info)
        if len(l_depends_not_installed) > 0:
            log_step(logger, header, "")
            logger.write(src.printcolors.printcError(
                    _("ERROR : the following product(s) is(are) mandatory: ")))
            for prod_name in l_depends_not_installed:
                logger.write(src.printcolors.printcError(prod_name + " "))
            logger.write("\n")
            continue
        
        # Call the function to compile the product
        res_prod, len_end_line, error_step = compile_product(sat,
                                                             p_name_info,
                                                             config,
                                                             options,
                                                             logger,
                                                             header,
                                                             len_end_line)
        
        if res_prod != 0:
            # Clean the install directory if there is any
            logger.write(_("Cleaning the install directory if there is any\n"),
                         5)
            sat.clean(config.VARS.application + 
                      " --products " + p_name + 
                      " --install",
                      batch=True,
                      verbose=0,
                      logger_add_link = logger)
            res += 1
            
        # Log the result
        if res_prod > 0:
            logger.write("\r%s%s" % (header, " " * len_end_line), 3)
            logger.write("\r" + header + src.printcolors.printcError("KO ") + error_step)
            logger.write("\n==== %(KO)s in compile of %(name)s \n" %
                { "name" : p_name , "KO" : src.printcolors.printcInfo("ERROR")}, 4)
            logger.flush()
        else:
            logger.write("\r%s%s" % (header, " " * len_end_line), 3)
            logger.write("\r" + header + src.printcolors.printcSuccess("OK"))
            logger.write(_("\nINSTALL directory = %s" % 
                           src.printcolors.printcInfo(p_info.install_dir)), 3)
            logger.write("\n==== %s \n" % src.printcolors.printcInfo("OK"), 4)
            logger.write("\n==== Compilation of %(name)s %(OK)s \n" %
                { "name" : p_name , "OK" : src.printcolors.printcInfo("OK")}, 4)
            logger.flush()
        logger.write("\n", 3, False)
        
        
        if res_prod != 0 and options.stop_first_fail:
            break
        
    return res

def compile_product(sat, p_name_info, config, options, logger, header, len_end):
    '''Execute the proper configuration command(s) 
       in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :return: 1 if it fails, else 0.
    :rtype: int
    '''
    
    p_name, p_info = p_name_info
       
    # Execute "sat configure", "sat make" and "sat install"
    res = 0
    error_step = ""
    
    # Logging and sat command call for configure step
    len_end_line = len_end
    log_step(logger, header, "CONFIGURE")
    res_c = sat.configure(config.VARS.application + " --products " + p_name,
                          verbose = 0,
                          logger_add_link = logger)
    log_res_step(logger, res_c)
    res += res_c
    
    if res_c > 0:
        error_step = "CONFIGURE"
    else:    
        # Logging and sat command call for make step
        # Logging take account of the fact that the product has a compilation 
        # script or not
        if src.product.product_has_script(p_info):
            # if the product has a compilation script, 
            # it is executed during make step
            scrit_path_display = src.printcolors.printcLabel(
                                                        p_info.compil_script)
            log_step(logger, header, "SCRIPT " + scrit_path_display)
            len_end_line = len(scrit_path_display)
        else:
            log_step(logger, header, "MAKE")
        make_arguments = config.VARS.application + " --products " + p_name
        # Get the make_flags option if there is any
        if options.makeflags:
            make_arguments += " --option -j" + options.makeflags
        res_m = sat.make(make_arguments,
                         verbose = 0,
                         logger_add_link = logger)
        log_res_step(logger, res_m)
        res += res_m
        
        if res_m > 0:
            error_step = "MAKE"
        else: 
            # Logging and sat command call for make install step
            log_step(logger, header, "MAKE INSTALL")
            res_mi = sat.makeinstall(config.VARS.application + 
                                     " --products " + 
                                     p_name,
                                    verbose = 0,
                                    logger_add_link = logger)

            log_res_step(logger, res_mi)
            res += res_mi
            
            if res_mi > 0:
                error_step = "MAKE INSTALL"

    # Check that the install directory exists
    if res==0 and not(os.path.exists(p_info.install_dir)):
        res = 1
        error_step = "NO INSTALL DIR"
        msg = _("Error: despite the fact that all the steps ended successfully,"
                " no install directory was found !")
        logger.write(src.printcolors.printcError(msg), 4)
        logger.write("\n", 4)
    
    # Add the config file corresponding to the dependencies/versions of the 
    # product that have been successfully compiled
    if res==0:       
        logger.write(_("Add the config file in installation directory\n"), 5)
        add_compile_config_file(p_info, config)
    
    return res, len_end_line, error_step

def add_compile_config_file(p_info, config):
    '''Execute the proper configuration command(s) 
       in the product build directory.
    
    :param p_info Config: The specific config of the product
    :param config Config: The global configuration
    '''
    # Create the compile config
    compile_cfg = src.pyconf.Config()
    for prod_name in p_info.depend:
        if prod_name not in compile_cfg:
            compile_cfg.addMapping(prod_name,
                                   src.pyconf.Mapping(compile_cfg),
                                   "")
        prod_dep_info = src.product.get_product_config(config, prod_name, False)
        compile_cfg[prod_name] = prod_dep_info.version
    # Write it in the install directory of the product
    compile_cfg_path = os.path.join(p_info.install_dir, src.CONFIG_FILENAME)
    f = open(compile_cfg_path, 'w')
    compile_cfg.__save__(f)
    f.close()
    
def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the compile command description.
    :rtype: str
    '''
    return _("The compile command constructs the products of the application"
             "\n\nexample:\nsat compile SALOME-master --products KERNEL,GUI,"
             "MEDCOUPLING --clean_all")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with compile parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # Warn the user if he invoked the clean_all option 
    # without --products option
    if (options.clean_all and 
        options.products is None and 
        not runner.options.batch):
        rep = input(_("You used --clean_all without specifying a product"
                          " are you sure you want to continue? [Yes/No] "))
        if rep.upper() != _("YES").upper():
            return 0
        
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Print some informations
    logger.write(_('Executing the compile commands in the build '
                                'directories of the products of '
                                'the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    
    info = [
            (_("SOURCE directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'SOURCES')),
            (_("BUILD directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'BUILD'))
            ]
    src.print_info(logger, info)

    # Get the list of products to treat
    products_infos = get_products_list(options, runner.cfg, logger)

    if options.fathers:
        # Extend the list with all recursive dependencies of the given products
        products_infos = extend_with_fathers(runner.cfg, products_infos)

    if options.children:
        # Extend the list with all products that use the given products
        products_infos = extend_with_children(runner.cfg, products_infos)

    # Sort the list regarding the dependencies of the products
    products_infos = sort_products(runner.cfg, products_infos)

    
    # Call the function that will loop over all the products and execute
    # the right command(s)
    res = compile_all_products(runner, runner.cfg, options, products_infos, logger)
    
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
    
    code = res
    if code != 0:
        code = 1
    return code