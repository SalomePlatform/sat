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
import subprocess
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


# from sat product infos, represent the product dependencies in a simple python graph
# keys are nodes, the list of dependencies are values
def get_dependencies_graph(p_infos):
    graph={}
    for (p_name,p_info) in p_infos:
        graph[p_name]=p_info.depend
    return graph

# this recursive function calculates all the dependencies of node start
def depth_search_graph(graph, start, visited=[]):
    visited= visited+ [start]
    for node in graph[start]:  # for all nodes in start dependencies
        if node not in visited:
            visited=depth_search_graph(graph, node, visited)
    return visited

# find a path from start node to end (a group of nodes)
def find_path_graph(graph, start, end, path=[]):
    path = path + [start]
    if start in end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path_graph(graph, node, end, path)
            if newpath: return newpath
    return None

# Topological sorting algo
# return in sorted_nodes the list of sorted nodes
def depth_first_topo_graph(graph, start, visited=[], sorted_nodes=[]):
    visited = visited + [start]
    for node in graph[start]:
        if node not in visited:
            visited,sorted_nodes=depth_first_topo_graph(graph, node, visited,sorted_nodes)
        else:
            assert node in sorted_nodes, 'Error : cycle detection for node %s and %s !' % (start,node)
    
    sorted_nodes = sorted_nodes + [start]
    return visited,sorted_nodes


# check for p_name that all dependencies are installed
def check_dependencies(config, p_name_p_info, all_products_dict):
    l_depends_not_installed = []
    for prod in p_name_p_info[1]["depend_all"]:
        # for each dependency, check the install
        prod_name, prod_info=all_products_dict[prod]
        if not(src.product.check_installation(prod_info)):
            l_depends_not_installed.append(prod_name)
    return l_depends_not_installed   # non installed deps

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

def compile_all_products(sat, config, options, products_infos, all_products_dict, logger):
    '''Execute the proper configuration commands 
       in each product build directory.

    :param config Config: The global configuration
    :param products_info list: List of 
                                 (str, Config) => (product_name, product_info)
    :param all_products_dict: Dict of all products 
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

        # Do nothing if the product is fixed (already compiled by third party)
        if src.product.product_is_fixed(p_info):
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
            for prod in all_products_dict:
                product_name, product_info = all_products_dict[prod]
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
        l_depends_not_installed = check_dependencies(config, p_name_info, all_products_dict)
        if len(l_depends_not_installed) > 0:
            log_step(logger, header, "")
            logger.write(src.printcolors.printcError(
                    _("ERROR : the following mandatory product(s) is(are) not installed: ")))
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

    
    # check if pip should be used : the application and product have pip property
    if (src.appli_test_property(config,"pip", "yes") and 
       src.product.product_test_property(p_info,"pip", "yes")):
            res, len_end_line, error_step = compile_product_pip(sat,
                                                                p_name_info,
                                                                config,
                                                                options,
                                                                logger,
                                                                header,
                                                                len_end)
    else:
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


def compile_product_pip(sat,
                        p_name_info,
                        config,
                        options,
                        logger,
                        header,
                        len_end):
    '''Execute the proper build procedure for pip products
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
    pip_install_in_python=False
    if src.appli_test_property(config,"pip_install_dir", "python"):
        # pip will install product in python directory"
        pip_install_cmd="pip3 install --disable-pip-version-check --no-index --find-links=%s --build %s %s==%s" %\
        (config.LOCAL.archive_dir, p_info.build_dir, p_name, p_info.version)
        pip_install_in_python=True
        
    else: 
        # pip will install product in product install_dir
        pip_install_dir=os.path.join(p_info.install_dir, "lib", "python${PYTHON_VERSION:0:3}", "site-packages")
        pip_install_cmd="pip3 install --disable-pip-version-check --no-index --find-links=%s --build %s --target %s %s==%s" %\
        (config.LOCAL.archive_dir, p_info.build_dir, pip_install_dir, p_name, p_info.version)
    log_step(logger, header, "PIP")
    logger.write("\n"+pip_install_cmd+"\n", 4)
    len_end_line = len_end + 3
    error_step = ""
    build_environ = src.environment.SalomeEnviron(config,
                             src.environment.Environ(dict(os.environ)),
                             True)
    environ_info = src.product.get_product_dependencies(config,
                                                        p_info)
    build_environ.silent = (config.USER.output_verbose_level < 5)
    build_environ.set_full_environ(logger, environ_info)
    
    if pip_install_in_python and (options.clean_install or options.clean_all):
        # for products installed by pip inside python install dir
        # finish the clean by uninstalling the product from python install dir
        pip_clean_cmd="pip3 uninstall -y  %s==%s" % (p_name, p_info.version)
        res_pipclean = (subprocess.call(pip_clean_cmd, 
                                   shell=True, 
                                   cwd=config.LOCAL.workdir,
                                   env=build_environ.environ.environ,
                                   stdout=logger.logTxtFile, 
                                   stderr=subprocess.STDOUT) == 0)        
        if not res_pipclean:
            logger.write("\n",1)
            logger.warning("pip3 uninstall failed!")

    res_pip = (subprocess.call(pip_install_cmd, 
                               shell=True, 
                               cwd=config.LOCAL.workdir,
                               env=build_environ.environ.environ,
                               stdout=logger.logTxtFile, 
                               stderr=subprocess.STDOUT) == 0)        
    if res_pip:
        res=0
        if pip_install_in_python:
            # when product is installed in python, create install_dir 
            # (to put inside product info and mark the installation success)
            os.mkdir(p_info.install_dir)
    else:
        #log_res_step(logger, res)
        res=1
        error_step = "PIP"

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

    # Get the list of all application products, and create its dependency graph
    all_products_infos = src.product.get_products_infos(runner.cfg.APPLICATION.products,
                                                        runner.cfg)
    all_products_graph=get_dependencies_graph(all_products_infos)
    logger.write("Dependency graph of all application products : %s\n" % all_products_graph, 6)

    # Get the list of products we have to compile
    products_infos = src.product.get_products_list(options, runner.cfg, logger)
    products_list = [pi[0] for pi in products_infos]

    logger.write("Product we have to compile (as specified by user) : %s\n" % products_list, 5)
    if options.fathers:
        # Extend the list with all recursive dependencies of the given products
        visited=[]
        for p_name in products_list:
            visited=depth_search_graph(all_products_graph, p_name, visited)
        products_list = visited

    logger.write("Product list to compile with fathers : %s\n" % products_list, 5)
    if options.children:
        # Extend the list with all products that depends upon the given products
        children=[]
        for n in all_products_graph:
            # for all products (that are not in products_list):
            # if we we find a path from the product to the product list,
            # then we product is a child and we add it to the children list 
            if (n not in children) and (n not in products_list):
                if find_path_graph(all_products_graph, n, products_list):
                    children = children + [n]
        # complete products_list (the products we have to compile) with the list of children
        products_list = products_list + children
        logger.write("Product list to compile with children : %s\n" % products_list, 5)

    # Sort the list of all products (topological sort).
    # the products listed first do not depend upon products listed after
    visited_nodes=[]
    sorted_nodes=[]
    for n in all_products_graph:
        if n not in visited_nodes:
            visited_nodes,sorted_nodes=depth_first_topo_graph(all_products_graph, n, visited_nodes,sorted_nodes)
    logger.write("Complete depndency graph topological search (sorting): %s\n" % sorted_nodes, 6)

#   use the sorted list of all products to sort the list of products we have to compile
    sorted_product_list=[]
    for n in sorted_nodes:
        if n in products_list:
            sorted_product_list.append(n)
    logger.write("Sorted list of products to compile : %s\n" % sorted_product_list, 5)

    
    # from the sorted list of products to compile, build a sorted list of products infos
    #  a- create a dict to facilitate products_infos sorting
    all_products_dict={}
    for (pname,pinfo) in all_products_infos:
        all_products_dict[pname]=(pname,pinfo)
    #  b- build a sorted list of products infos in products_infos
    products_infos=[]
    for product in sorted_product_list:
        products_infos.append(all_products_dict[product])

    # for all products to compile, store in "depend_all" field the complete dependencies (recursive) 
    # (will be used by check_dependencies funvtion)
    for pi in products_infos:
        dep_prod=[]
        dep_prod=depth_search_graph(all_products_graph,pi[0], dep_prod)
        pi[1]["depend_all"]=dep_prod[1:]
        

    # Call the function that will loop over all the products and execute
    # the right command(s)
    res = compile_all_products(runner, runner.cfg, options, products_infos, all_products_dict, logger)
    
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
