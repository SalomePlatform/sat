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
import re
import src
import src.debug as DBG

# Compatibility python 2/3 for input function
# input stays input for python 3 and input = raw_input for python 2
try: 
    input = raw_input
except NameError: 
    pass


# Define all possible option for the compile command :  sat compile <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to compile. This option accepts a comma separated list.'))
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
parser.add_option('', 'check', 'boolean', 'check', _(
                  "Optional: execute the unit tests after compilation"), False)

parser.add_option('', 'clean_build_after', 'boolean', 'clean_build_after', 
                  _('Optional: remove the build directory after successful compilation'), False)


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
        header = _("Compilation of %s") % src.printcolors.printcLabel(p_name)
        header += " %s " % ("." * (len_end_line - len(p_name)))
        logger.write(header, 3)
        logger.flush()

        # Do nothing if the product is not compilable
        if not src.product.product_compiles(p_info):
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
            log_step(logger, header, "CLEAN BUILD AND INSTALL ")
            sat.clean(config.VARS.application + 
                      " --products " + p_name + 
                      " --build --install",
                      batch=True,
                      verbose=0,
                      logger_add_link = logger)

        # DBG.write("Only for test of check_config_exists", src.product.check_config_exists(config, "/volatile/wambeke/SAT5/MATIX_V24_S840/INSTALL/PACKAGESPY", p_info, verbose=True), True)

        # Clean the the install directory 
        # if the corresponding option was called
        if options.clean_install and not options.clean_all:
            log_step(logger, header, "CLEAN INSTALL ")
            sat.clean(config.VARS.application + 
                      " --products " + p_name + 
                      " --install",
                      batch=True,
                      verbose=0,
                      logger_add_link = logger)
        
        # Recompute the product information to get the right install_dir
        # (it could change if there is a clean of the install directory)
        p_info = src.product.get_product_config(config, p_name)
        
        # Check if sources was already successfully installed
        check_source = src.product.check_source(p_info)
        if not options.no_compile: # don't check sources with option --show!
            if not check_source:
                logger.write(_("Sources of product not found (try 'sat -h prepare') \n"))
                res += 1 # one more error
                continue
        
        if src.product.product_is_salome(p_info):
            # For salome modules, we check if the sources of configuration modules are present
            # configuration modules have the property "configure_dependency"

            # get the list of all modules in application 
            all_products_infos = src.product.get_products_infos(config.APPLICATION.products,
                                                                config)
            check_source = True
            # for configuration modules, check if sources are present
            for product_name, product_info in all_products_infos:
                if ("properties" in product_info and
                    "configure_dependency" in product_info.properties and
                    product_info.properties.configure_dependency == "yes"):
                    check_source = check_source and src.product.check_source(product_info)
                    if not check_source:
                        logger.write(_("\nERROR : SOURCES of %s not found! It is required for" 
                                       " the configuration\n" % product_name))
                        logger.write(_("        Get it with the command : sat prepare %s -p %s \n" % 
                                      (config.APPLICATION.name, product_name)))
            if not check_source:
                # if at least one configuration module is not present, we stop compilation
                res += 1
                continue
        
        # Check if it was already successfully installed
        if src.product.check_installation(p_info):
            logger.write(_("Already installed"))
            logger.write(_(" in %s" % p_info.install_dir), 4)
            logger.write(_("\n"))
            continue
        
        # If the show option was called, do not launch the compilation
        if options.no_compile:
            logger.write(_("Not installed in %s\n" % p_info.install_dir))
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
        res_prod, len_end_line, error_step = compile_product(
             sat, p_name_info, config, options, logger, header, len_end_line)
        
        if res_prod != 0:
            res += 1
            
            if error_step != "CHECK":
                # Clean the install directory if there is any
                logger.write(_(
                            "Cleaning the install directory if there is any\n"),
                             5)
                sat.clean(config.VARS.application + 
                          " --products " + p_name + 
                          " --install",
                          batch=True,
                          verbose=0,
                          logger_add_link = logger)
        else:
            # Clean the build directory if the compilation and tests succeed
            if options.clean_build_after:
                log_step(logger, header, "CLEAN BUILD")
                sat.clean(config.VARS.application + 
                          " --products " + p_name + 
                          " --build",
                          batch=True,
                          verbose=0,
                          logger_add_link = logger)

        # Log the result
        if res_prod > 0:
            logger.write("\r%s%s" % (header, " " * len_end_line), 3)
            logger.write("\r" + header + src.printcolors.printcError("KO ") + error_step)
            logger.write("\n==== %(KO)s in compile of %(name)s \n" %
                { "name" : p_name , "KO" : src.printcolors.printcInfo("ERROR")}, 4)
            if error_step == "CHECK":
                logger.write(_("\nINSTALL directory = %s" % 
                           src.printcolors.printcInfo(p_info.install_dir)), 3)
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
    :param header Str: the header to display when logging
    :param len_end Int: the lenght of the the end of line (used in display)
    :return: 1 if it fails, else 0.
    :rtype: int
    '''
    
    p_name, p_info = p_name_info
          
    # Get the build procedure from the product configuration.
    # It can be :
    # build_sources : autotools -> build_configure, configure, make, make install
    # build_sources : cmake     -> cmake, make, make install
    # build_sources : script    -> script executions
    res = 0
    if (src.product.product_is_autotools(p_info) or 
                                          src.product.product_is_cmake(p_info)):
        res, len_end_line, error_step = compile_product_cmake_autotools(sat,
                                                                  p_name_info,
                                                                  config,
                                                                  options,
                                                                  logger,
                                                                  header,
                                                                  len_end)
    if src.product.product_has_script(p_info):
        res, len_end_line, error_step = compile_product_script(sat,
                                                                  p_name_info,
                                                                  config,
                                                                  options,
                                                                  logger,
                                                                  header,
                                                                  len_end)

    # Check that the install directory exists
    if res==0 and not(os.path.exists(p_info.install_dir)):
        res = 1
        error_step = "NO INSTALL DIR"
        msg = _("Error: despite the fact that all the steps ended successfully,"
                " no install directory was found !")
        logger.write(src.printcolors.printcError(msg), 4)
        logger.write("\n", 4)
        return res, len_end, error_step
    
    # Add the config file corresponding to the dependencies/versions of the 
    # product that have been successfully compiled
    if res==0:       
        logger.write(_("Add the config file in installation directory\n"), 5)
        src.product.add_compile_config_file(p_info, config)
        
        if options.check:
            # Do the unit tests (call the check command)
            log_step(logger, header, "CHECK")
            res_check = sat.check(
                              config.VARS.application + " --products " + p_name,
                              verbose = 0,
                              logger_add_link = logger)
            if res_check != 0:
                error_step = "CHECK"
                
            res += res_check
    
    return res, len_end_line, error_step

def compile_product_cmake_autotools(sat,
                                    p_name_info,
                                    config,
                                    options,
                                    logger,
                                    header,
                                    len_end):
    '''Execute the proper build procedure for autotools or cmake
       in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param header Str: the header to display when logging
    :param len_end Int: the lenght of the the end of line (used in display)
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
                
    return res, len_end_line, error_step 

def compile_product_script(sat,
                           p_name_info,
                           config,
                           options,
                           logger,
                           header,
                           len_end):
    '''Execute the script build procedure in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :param header Str: the header to display when logging
    :param len_end Int: the lenght of the the end of line (used in display)
    :return: 1 if it fails, else 0.
    :rtype: int
    '''
    p_name, p_info = p_name_info
    
    # Execute "sat configure", "sat make" and "sat install"
    error_step = ""
    
    # Logging and sat command call for the script step
    scrit_path_display = src.printcolors.printcLabel(p_info.compil_script)
    log_step(logger, header, "SCRIPT " + scrit_path_display)
    len_end_line = len_end + len(scrit_path_display)
    res = sat.script(config.VARS.application + " --products " + p_name,
                     verbose = 0,
                     logger_add_link = logger)
    log_res_step(logger, res)
              
    return res, len_end_line, error_step 

    
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
    # DBG.write("compile runner.cfg", runner.cfg, True)
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
    products_infos = src.product.get_products_list(options, runner.cfg, logger)

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
