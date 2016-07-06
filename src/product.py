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
'''In this file are implemented the classes and methods 
   relative to the product notion of salomeTools
'''

import os

import src

AVAILABLE_VCS = ['git', 'svn', 'cvs']

def get_product_config(config, product_name):
    '''Get the specific configuration of a product from the global configuration
    
    :param config Config: The global configuration
    :param product_name str: The name of the product
    :return: the specific configuration of the product
    :rtype: Config
    '''
    
    # Get the version of the product from the application definition
    version = config.APPLICATION.products[product_name]
    # if no version, then take the default one defined in the application
    if isinstance(version, bool): 
        version = config.APPLICATION.tag      
    
    # Define debug and dev modes
    # Get the tag if a dictionary is given in APPLICATION.products for the
    # current product 
    debug = 'no'
    dev = 'no'
    if isinstance(version, src.pyconf.Mapping):
        dic_version = version
        # Get the version/tag
        if not 'tag' in dic_version:
            version = config.APPLICATION.tag
        else:
            version = dic_version.tag
        
        # Get the debug if any
        if 'debug' in dic_version:
            debug = dic_version.debug
        
        # Get the dev if any
        if 'dev' in dic_version:
            dev = dic_version.dev
    
    vv = version
    # substitute some character with _ in order to get the correct definition
    # in config.PRODUCTS. This is done because the pyconf tool does not handle
    # the . and - characters 
    for c in ".-": vv = vv.replace(c, "_")
    
    prod_info = None
    if product_name in config.PRODUCTS:
        # If it exists, get the information of the product_version
        if "version_" + vv in config.PRODUCTS[product_name]:
            # returns specific information for the given version
            prod_info = config.PRODUCTS[product_name]["version_" + vv]    
        # Get the standard informations
        elif "default" in config.PRODUCTS[product_name]:
            # returns the generic information (given version not found)
            prod_info = config.PRODUCTS[product_name].default
        
        # merge opt_depend in depend
        if prod_info is not None and 'opt_depend' in prod_info:
            for depend in prod_info.opt_depend:
                if depend in config.PRODUCTS:
                    prod_info.depend.append(depend,'')
        
        # In case of a product get with a vcs, 
        # put the tag (equal to the version)
        if prod_info is not None and prod_info.get_source in AVAILABLE_VCS:
            
            if prod_info.get_source == 'git':
                prod_info.git_info.tag = version
            
            if prod_info.get_source == 'svn':
                prod_info.svn_info.tag = version
            
            if prod_info.get_source == 'cvs':
                prod_info.cvs_info.tag = version
        
        # In case of a fixed product, 
        # define the install_dir (equal to the version)
        if prod_info is not None and prod_info.get_source=="fixed":
            prod_info.install_dir = version
        
        # Check if the product is defined as native in the application
        if prod_info is not None:
            if version == "native":
                prod_info.get_source = "native"
            elif prod_info.get_source == "native":
                msg = _("The product %(prod)s has version %(ver)s but is "
                        "declared as native in its definition" %
                        { 'prod': prod_info.name, 'ver': version})
                raise src.SatException(msg)

    # If there is no definition but the product is declared as native,
    # construct a new definition containing only the get_source key
    if prod_info is None and version == "native":
        prod_info = src.pyconf.Config()
        prod_info.name = product_name
        prod_info.get_source = "native"
    
    # If prod_info is still None, it means that there is no product definition
    # in the config. The user has to provide it.
    if prod_info is None:
        msg = _("No definition found for the product %s\n"
            "Please create a %s.pyconf file." % (product_name, product_name))
        raise src.SatException(msg)
    
    # Set the debug, dev and version keys
    prod_info.debug = debug
    prod_info.dev = dev
    prod_info.version = version
    
    # Set the archive_info if the product is get in archive mode
    if prod_info.get_source == "archive":
        if not "archive_info" in prod_info:
            prod_info.addMapping("archive_info",
                                 src.pyconf.Mapping(prod_info),
                                 "")
        if "archive_name" not in prod_info.archive_info: 
            arch_name = product_name + "-" + version + ".tar.gz"
            arch_path = src.find_file_in_lpath(arch_name,
                                               config.PATHS.ARCHIVEPATH)
            if not arch_path:
                msg = _("Archive %(arch_name)s for %(prod_name)s not found:"
                            "\n" % {"arch_name" : arch_name,
                                     "prod_name" : prod_info.name}) 
                raise src.SatException(msg)
            prod_info.archive_info.archive_name = arch_path
        else:
            if (os.path.basename(prod_info.archive_info.archive_name) == 
                                        prod_info.archive_info.archive_name):
            
                arch_path = src.find_file_in_lpath(
                                            prod_info.archive_info.archive_name,
                                            config.PATHS.ARCHIVEPATH)
                if not arch_path:
                    msg = _("Archive %(arch_name)s for %(prod_name)s not found:"
                                "\n" % {"arch_name" : arch_name,
                                         "prod_name" : prod_info.name}) 
                    raise src.SatException(msg)
                prod_info.archive_info.archive_name = arch_path
    
    # Set the install_dir key
    if "install_dir" not in prod_info:
        # Set it to the default value (in application directory)
        prod_info.install_dir = os.path.join(config.APPLICATION.workdir,
                                            "INSTALL",
                                            prod_info.name)
    else:
        if prod_info.install_dir == "base":
            # Get the product base of the application
            base_path = src.get_base_path(config) 
            prod_info.install_dir = os.path.join(base_path,
                                            prod_info.name + "-" + version)
    
    # If the product compiles with a script, check the script existence
    # and if it is executable
    if product_has_script(prod_info):
        # Check the compil_script key existence
        if "compil_script" not in prod_info:
            msg = _("No compilation script found for the product %s\n"
                "Please provide a \"compil_script\" key in its definition." 
                % (product_name))
            raise src.SatException(msg)
        
        # Get the path of the script
        script = prod_info.compil_script
        script_name = os.path.basename(script)
        if script == script_name:
            # Only a name is given. Search in the default directory
            script_path = src.find_file_in_lpath(script_name,
                                                 config.PATHS.PRODUCTPATH,
                                                 "compil_scripts")
            prod_info.compil_script = script_path

        # Check script existence
        if not os.path.exists(prod_info.compil_script):
            raise src.SatException(_("Compilation script not found: %s") % 
                                   prod_info.compil_script)
        
        # Check that the script is executable
        if not os.access(prod_info.compil_script, os.X_OK):
            raise src.SatException(
                    _("Compilation script cannot be executed: %s") % 
                    prod_info.compil_script)
    
    # Get the full paths of all the patches
    if "patches" in prod_info:
        patches = []
        for patch in prod_info.patches:
            patch_path = patch
            # If only a filename, then search for the patch in the PRODUCTPATH
            if os.path.basename(patch_path) == patch_path:
                # Search in the PRODUCTPATH/patches
                patch_path = src.find_file_in_lpath(patch,
                                                    config.PATHS.PRODUCTPATH,
                                                    "patches")
                if not patch_path:
                    msg = _("Patch %(patch_name)s for %(prod_name)s not found:"
                            "\n" % {"patch_name" : patch,
                                     "prod_name" : prod_info.name}) 
                    raise src.SatException(msg)
            patches.append(patch_path)
        prod_info.patches = patches

    # Get the full paths of the environment scripts
    if "environ" in prod_info and "env_script" in prod_info.environ:
        env_script_path = prod_info.environ.env_script
        # If only a filename, then search for the environment script 
        # in the PRODUCTPATH/env_scripts
        if os.path.basename(env_script_path) == env_script_path:
            # Search in the PRODUCTPATH/env_scripts
            env_script_path = src.find_file_in_lpath(
                                            prod_info.environ.env_script,
                                            config.PATHS.PRODUCTPATH,
                                            "env_scripts")
            if not env_script_path:
                msg = _("Environment script %(env_name)s for %(prod_name)s not "
                        "found.\n" % {"env_name" : env_script_path,
                                       "prod_name" : prod_info.name}) 
                raise src.SatException(msg)

        prod_info.environ.env_script = env_script_path
                    
    return prod_info

def get_products_infos(lproducts, config):
    '''Get the specific configuration of a list of products
    
    :param lproducts List: The list of product names
    :param config Config: The global configuration
    :return: the list of tuples 
             (product name, specific configuration of the product)
    :rtype: [(str, Config)]
    '''
    products_infos = []
    # Loop on product names
    for prod in lproducts:       
        # Get the specific configuration of the product
        prod_info = get_product_config(config, prod)
        if prod_info is not None:
            products_infos.append((prod, prod_info))
        else:
            msg = _("The %s product has no definition "
                    "in the configuration.") % prod
            raise src.SatException(msg)
    return products_infos

def get_product_dependencies(config, product_info):
    '''Get recursively the list of products that are 
       in the product_info dependencies
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product
    :return: the list of products in dependence
    :rtype: list
    '''
    if "depend" not in product_info or product_info.depend == []:
        return []
    res = []
    for prod in product_info.depend:
        if prod not in res:
            res.append(prod)
        prod_info = get_product_config(config, prod)
        dep_prod = get_product_dependencies(config, prod_info)
        for prod_in_dep in dep_prod:
            if prod_in_dep not in res:
                res.append(prod_in_dep)
    return res

def check_installation(product_info):
    '''Verify if a product is well installed. Checks install directory presence
       and some additional files if it is defined in the config 
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if it is well installed
    :rtype: boolean
    '''
    install_dir = product_info.install_dir
    if not os.path.exists(install_dir):
        return False
    if ("present_files" in product_info and 
        "install" in product_info.present_files):
        for file_relative_path in product_info.present_files.install:
            file_path = os.path.join(install_dir, file_relative_path)
            if not os.path.exists(file_path):
                return False
    return True

def product_is_sample(product_info):
    '''Know if a product has the sample type
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has the sample type, else False
    :rtype: boolean
    '''
    if 'type' in product_info:
        ptype = product_info.type
        return ptype.lower() == 'sample'
    else:
        return False

def product_is_salome(product_info):
    '''Know if a product is of type salome
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is salome, else False
    :rtype: boolean
    '''
    if 'type' in product_info:
        ptype = product_info.type
        return ptype.lower() == 'salome'
    else:
        return False

def product_is_fixed(product_info):
    '''Know if a product is fixed
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is fixed, else False
    :rtype: boolean
    '''
    get_src = product_info.get_source
    return get_src.lower() == 'fixed'

def product_is_native(product_info):
    '''Know if a product is native
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is native, else False
    :rtype: boolean
    '''
    get_src = product_info.get_source
    return get_src.lower() == 'native'

def product_is_dev(product_info):
    '''Know if a product is in dev mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in dev mode, else False
    :rtype: boolean
    '''
    dev = product_info.dev
    return dev.lower() == 'yes'

def product_is_debug(product_info):
    '''Know if a product is in debug mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in debug mode, else False
    :rtype: boolean
    '''
    debug = product_info.debug
    return debug.lower() == 'yes'

def product_is_autotools(product_info):
    '''Know if a product is compiled using the autotools
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is autotools, else False
    :rtype: boolean
    '''
    build_src = product_info.build_source
    return build_src.lower() == 'autotools'

def product_is_cmake(product_info):
    '''Know if a product is compiled using the cmake
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is cmake, else False
    :rtype: boolean
    '''
    build_src = product_info.build_source
    return build_src.lower() == 'cmake'

def product_has_script(product_info):
    '''Know if a product has a compilation script
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product it has a compilation script, else False
    :rtype: boolean
    '''
    if "build_source" not in product_info:
        # Native case
        return False
    build_src = product_info.build_source
    return build_src.lower() == 'script'