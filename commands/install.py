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
import shutil
import re
import subprocess

import src
import prepare
import src.debug as DBG

PACKAGE_EXT=".tar.gz" # the extension we use for the packages

# Define all possible option for patch command :  sat patch <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products from which to get the sources. This option accepts a comma separated list.'))


def get_binary_from_archive(config, product_name, product_info, install_dir, logger):
    '''The method get the binary of the product from an archive
    
    :param config Config: The global configuration
    :param product_name : The name of the product
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param install_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :return: True if it succeed, else False
    :rtype: boolean
    '''


    # check archive exists

    # the expected name of the bin archive, as produced by sat package --bin_products
    archive_name = product_name + '-' + product_info.version + "-" + config.VARS.dist + PACKAGE_EXT
    # we search this archive in bin directory
    bin_arch_name = os.path.join("bin",archive_name)
    # search in the config.PATHS.ARCHIVEPATH
    arch_path = src.find_file_in_lpath(archive_name, config.PATHS.ARCHIVEPATH, "bin")
    if not arch_path:
        # bin archive was not found locally in ARCHIVEPATH
        # search on ftp site
        logger.write("\n   The bin archive is not found on local file system, we try ftp\n", 3)
        ret=src.find_file_in_ftppath(bin_arch_name, config.PATHS.ARCHIVEFTP, 
                                     config.LOCAL.archive_dir, logger)
        
        if ret:
            # archive was found on ftp and stored in ret
            arch_path = ret
        else:
            logger.write('%s  ' % src.printcolors.printc(src.OK_STATUS), 3, False) 
            msg = _("Archive not found in ARCHIVEPATH, nor on ARCHIVEFTP: '%s'") % bin_arch_name
            logger.write(msg, 3)
            return 1

    logger.write('arc:%s ... ' % 
                 src.printcolors.printcInfo(archive_name),
                 3, 
                 False)
    logger.flush()
    # Call the system function that do the extraction in archive mode
    retcode, NameExtractedDirectory = src.system.archive_extract(arch_path,
                                      install_dir.dir(), logger)
    
    # Rename the source directory if 
    # it does not match with product_info.source_dir
    if (NameExtractedDirectory.replace('/', '') != 
            os.path.basename(product_info.install_dir)):
        shutil.move(os.path.join(os.path.dirname(product_info.install_dir), 
                                 NameExtractedDirectory), 
                    product_info.install_dir)
    
    return retcode


def get_product_binaries(config, 
                         product_info, 
                         is_dev, 
                         source_dir,
                         logger, 
                         pad, 
                         checkout=False):
    '''Get the product binaries.
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param is_dev boolean: True if the product is in development mode
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :param checkout boolean: If True, get the source in checkout mode
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    
    # Get the application environment
    logger.write(_("Set the application environment\n"), 5)
    env_appli = src.environment.SalomeEnviron(config,
                                      src.environment.Environ(dict(os.environ)))
    env_appli.set_application_env(logger)
    
    # Call the right function to get sources regarding the product settings
    if not checkout and is_dev:
        return get_source_for_dev(config, 
                                   product_info, 
                                   source_dir, 
                                   logger, 
                                   pad)

    if product_info.get_source == "git":
        return get_source_from_git(config, product_info, source_dir, logger, pad, 
                                    is_dev,env_appli)

    if product_info.get_source == "archive":
        return get_source_from_archive(config, product_info, source_dir, logger)

    if product_info.get_source == "dir":
        return get_source_from_dir(product_info, source_dir, logger)
    
    if product_info.get_source == "cvs":
        cvs_user = config.USER.cvs_user
        return get_source_from_cvs(cvs_user, 
                                    product_info, 
                                    source_dir, 
                                    checkout, 
                                    logger,
                                    pad,
                                    env_appli)

    if product_info.get_source == "svn":
        svn_user = config.USER.svn_user
        return get_source_from_svn(svn_user, product_info, source_dir, 
                                    checkout,
                                    logger,
                                    env_appli)

    if product_info.get_source == "native":
        # for native products we check the corresponding system packages are installed
        logger.write("Native : Checking system packages are installed\n" , 3)
        check_cmd=src.system.get_pkg_check_cmd(config.VARS.dist_name) # (either rmp or apt)
        run_pkg,build_pkg=src.product.check_system_dep(config.VARS.dist, check_cmd, product_info)
        result=True
        for pkg in run_pkg:
            logger.write(" - "+pkg + " : " + run_pkg[pkg], 1)
            if "KO" in run_pkg[pkg]:
                result=False
        for pkg in build_pkg:
            logger.write(" - "+pkg + " : " + build_pkg[pkg], 1)
            if "KO" in build_pkg[pkg]:
                result=False
        if result==False:
            logger.error("some system dependencies are missing, please install them with "+\
                         check_cmd[0])
        return result        

    if product_info.get_source == "fixed":
        # skip
        logger.write('%s  ' % src.printcolors.printc(src.OK_STATUS),
                     3,
                     False)
        msg = "FIXED : %s\n" % product_info.install_dir

        if not os.path.isdir(product_info.install_dir):
            logger.warning("The fixed path do not exixts!! Please check it : %s\n" % product_info.install_dir)
        else:
            logger.write(msg, 3)
        return True  

    # if the get_source is not in [git, archive, cvs, svn, fixed, native]
    logger.write(_("Unknown get source method \"%(get)s\" for product %(product)s") % \
        { 'get': product_info.get_source, 'product': product_info.name }, 3, False)
    logger.write(" ... ", 3, False)
    logger.flush()
    return False

def get_all_product_binaries(config, products, logger):
    '''Get all the product sources.
    
    :param config Config: The global configuration
    :param products List: The list of tuples (product name, product informations)
    :param logger Logger: The logger instance to be used for the logging
    :return: the tuple (number of success, dictionary product_name/success_fail)
    :rtype: (int,dict)
    '''

    # Initialize the variables that will count the fails and success
    results = dict()
    good_result = 0

    # Get the maximum name length in order to format the terminal display
    max_product_name_len = 1
    if len(products) > 0:
        max_product_name_len = max(map(lambda l: len(l), products[0])) + 4
    
    # The loop on all the products from which to get the binaries
    for product_name, product_info in products:
        # display and log
        logger.write('%s: ' % src.printcolors.printcLabel(product_name), 3)
        logger.write(' ' * (max_product_name_len - len(product_name)), 3, False)
        logger.write("\n", 4, False)
        #
        do_install_prod=True
        # check if there is something to do!
        if src.product.product_is_fixed(product_info):
            do_install_prod=False
            msg = _("INFO : Not doing anything because the products %s is fixed\n") % product_name
        elif src.product.product_is_native(product_info):
            do_install_prod=False
            msg = _("INFO : Not doing anything because the products %s is native\n") % product_name
        elif src.appli_test_property(config,"pip", "yes") and \
             src.product.product_test_property(product_info,"pip", "yes"):
            do_install_prod=False
            msg = _("INFO : Not doing anything because the products %s is managed by pip\n") % product_name
        else:
            install_dir=src.Path(product_info.install_dir) 
            if install_dir.exists():
                do_install_prod=False 
                msg = _("INFO : Not doing anything because the install directory already exists:\n    %s\n") % install_dir

        if not do_install_prod:
            logger.write('%s  ' % src.printcolors.printc(src.OK_STATUS), 3, False) 
            logger.write(msg, 3)
            good_result = good_result + 1  
            # Do not get the binaries and go to next product
            continue

        # we neeed to install binaries for the product
        retcode = get_binary_from_archive(config, product_name, product_info, install_dir, logger)

        # Check that the sources are correctly get using the files to be tested
        # in product information
        if retcode:
            pass
            # CNC TODO check md5sum
            #check_OK, wrong_path = check_sources(product_info, logger)
            #if not check_OK:
            #    # Print the missing file path
            #    msg = _("The required file %s does not exists. " % wrong_path)
            #    logger.write(src.printcolors.printcError("\nERROR: ") + msg, 3)
            #    retcode = False
# does post install substitutions
#for f in $(grep -RIl -e /volatile/salome/jenkins/workspace/Salome_master_CO7/SALOME-9.7.0-CO7/INSTALL INSTALL); do
#     sed -i "
#        s?/volatile/salome/jenkins/workspace/Salome_master_CO7/SALOME-9.7.0-CO7/INSTALL?$(pwd)/INSTALL?g
#            " $f
#done


        # show results
        results[product_name] = retcode
        if retcode:
            # The case where it succeed
            res = src.OK_STATUS
            good_result = good_result + 1
        else:
            # The case where it failed
            res = src.KO_STATUS
        
        # print the result
        if do_install_prod:
            logger.write('%s\n' % src.printcolors.printc(res), 3, False)

    return good_result, results

def check_sources(product_info, logger):
    '''Check that the sources are correctly get, using the files to be tested
       in product information
    
    :param product_info Config: The configuration specific to 
                                the product to be prepared
    :return: True if the files exists (or no files to test is provided).
    :rtype: boolean
    '''
    # Get the files to test if there is any
    if ("present_files" in product_info and 
        "source" in product_info.present_files):
        l_files_to_be_tested = product_info.present_files.source
        for file_path in l_files_to_be_tested:
            # The path to test is the source directory 
            # of the product joined the file path provided
            path_to_test = os.path.join(product_info.source_dir, file_path)
            logger.write(_("\nTesting existence of file: \n"), 5)
            logger.write(path_to_test, 5)
            if not os.path.exists(path_to_test):
                return False, path_to_test
            logger.write(src.printcolors.printcSuccess(" OK\n"), 5)
    return True, ""

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the source command description.
    :rtype: str
    '''
    return _("The source command gets the sources of the application products "
             "from cvs, git or an archive.\n\nexample:"
             "\nsat source SALOME-master --products KERNEL,GUI")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with install parameter.
    '''
    DBG.write("install.run()", args)
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Print some informations
    logger.write(_('Getting binaries of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    src.printcolors.print_value(logger, 'workdir', 
                                runner.cfg.APPLICATION.workdir, 2)
    logger.write("\n", 2, False)
       

    # Get the list of all application products, and create its dependency graph
    all_products_infos = src.product.get_products_infos(runner.cfg.APPLICATION.products,
                                                        runner.cfg)
    from compile import get_dependencies_graph,depth_search_graph
    all_products_graph=get_dependencies_graph(all_products_infos)
    #logger.write("Dependency graph of all application products : %s\n" % all_products_graph, 6)
    DBG.write("Dependency graph of all application products : ", all_products_graph)

    products_infos=[]
    if options.products is None:
        #implicit selection of all products
        products_infos = all_products_infos
    else:
        # a list of products is specified
        products_list=options.products
        # we evaluate the complete list including dependencies (~ to the --with-fathers of sat compile)

        # Extend the list with all recursive dependencies of the given products
        visited=[]
        for p_name in products_list:
            visited=depth_search_graph(all_products_graph, p_name, visited)
        products_list = visited
        logger.write("Product we have to compile (as specified by user) : %s\n" % products_list, 5)

        #  Create a dict of all products to facilitate products_infos sorting
        all_products_dict={}
        for (pname,pinfo) in all_products_infos:
            all_products_dict[pname]=(pname,pinfo)

        # build products_infos for the products we have to install
        for product in products_list:
            products_infos.append(all_products_dict[product])


    
    # Call to the function that gets all the sources
    good_result, results = get_all_product_binaries(runner.cfg, 
                                                    products_infos,
                                                    logger)

    # Display the results (how much passed, how much failed, etc...)
    status = src.OK_STATUS
    details = []

    logger.write("\n", 2, False)
    if good_result == len(products_infos):
        res_count = "%d / %d" % (good_result, good_result)
    else:
        status = src.KO_STATUS
        res_count = "%d / %d" % (good_result, len(products_infos))

        for product in results:
            if results[product] == 0 or results[product] is None:
                details.append(product)

    result = len(products_infos) - good_result

    # write results
    logger.write(_("Getting binaries of the application:"), 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)

    if len(details) > 0:
        logger.write(_("Following binaries haven't been get:\n"), 2)
        logger.write(" ".join(details), 2)
        logger.write("\n", 2, False)

    return result
