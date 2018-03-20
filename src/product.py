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
'''In this file are implemented the methods 
   relative to the product notion of salomeTools
'''

import os
import re

import src
import src.debug as DBG

AVAILABLE_VCS = ['git', 'svn', 'cvs']
config_expression = "^config-\d+$"
VERSION_DELIMITER = "_to_"

def get_product_config(config, product_name, with_install_dir=True):
    '''Get the specific configuration of a product from the global configuration
    
    :param config Config: The global configuration
    :param product_name str: The name of the product
    :param with_install_dir boolean: If false, do not provide an install 
                                     directory (at false only for internal use 
                                     of the function check_config_exists)
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
    base = 'maybe'
    section = None
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
        
        # Get the base if any
        if 'base' in dic_version:
            base = dic_version.base

        # Get the section if any
        if 'section' in dic_version:
            section = dic_version.section
    
    vv = version
    # substitute some character with _ in order to get the correct definition
    # in config.PRODUCTS. This is done because the pyconf tool does not handle
    # the . and - characters 
    for c in ".-": vv = vv.replace(c, "_")
    
    prod_info = None
    if product_name in config.PRODUCTS:
        # Search for the product description in the configuration
        prod_info = get_product_section(config, product_name, vv, section)
        
        # merge opt_depend in depend
        if prod_info is not None and 'opt_depend' in prod_info:
            for depend in prod_info.opt_depend:
                if depend in config.APPLICATION.products:
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
        if prod_info is not None and os.path.isdir(version):
            prod_info.install_dir = version
            prod_info.get_source = "fixed"
        
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

    # If there is no definition but the product is fixed,
    # construct a new definition containing only the product name
    if prod_info is None and os.path.isdir(version):
        prod_info = src.pyconf.Config()
        prod_info.name = product_name
        prod_info.get_source = "fixed"
        prod_info.addMapping("environ", src.pyconf.Mapping(prod_info), "")


    # If prod_info is still None, it means that there is no product definition
    # in the config. The user has to provide it.
    if prod_info is None:
        prod_pyconf_path = src.find_file_in_lpath(product_name + ".pyconf",
                                                  config.PATHS.PRODUCTPATH)
        if not prod_pyconf_path:
            msg = _("""\
No definition found for the product %(1)s.
Please create a %(2)s.pyconf file somewhere in:
%(3)s""") % {
  "1": product_name, 
  "2": product_name,
  "3": config.PATHS.PRODUCTPATH }
        else:
            msg = _("""\
No definition corresponding to the version %(1)s was found in the file:
  %(2)s.
Please add a section in it.""") % {"1" : vv, "2" : prod_pyconf_path}
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
                msg = _("Archive %(1)s for %(2)s not found in config.PATHS.ARCHIVEPATH") % \
                       {"1" : arch_name, "2" : prod_info.name}
                DBG.tofix(msg, config.PATHS.ARCHIVEPATH)
                prod_info.archive_info.archive_name = arch_name #without path
                # raise src.SatException(msg) #may be a warning, continue #8646
            else:
                prod_info.archive_info.archive_name = arch_path
        else:
            if (os.path.basename(prod_info.archive_info.archive_name) == 
                                        prod_info.archive_info.archive_name):
                arch_name = prod_info.archive_info.archive_name
                arch_path = src.find_file_in_lpath(
                                            arch_name,
                                            config.PATHS.ARCHIVEPATH)
                if not arch_path:
                    msg = _("Archive %(1)s for %(2)s not found in config.PATHS.ARCHIVEPATH") % \
                           {"1" : arch_name, "2" : prod_info.name}
                    DBG.tofix(msg, config.PATHS.ARCHIVEPATH) #avoid 2 messages in compile
                    prod_info.archive_info.archive_name = arch_name #without path
                    # raise src.SatException(msg) #may be a warning, continue #8646
                prod_info.archive_info.archive_name = arch_path
        
    # If the product compiles with a script, check the script existence
    # and if it is executable
    if product_has_script(prod_info):
        # Check the compil_script key existence
        if "compil_script" not in prod_info:
            msg = _("""\
No compilation script found for the product %s.
Please provide a 'compil_script' key in its definition.""") % product_name
            raise src.SatException(msg)
        
        # Get the path of the script
        script = prod_info.compil_script
        script_name = os.path.basename(script)
        if script == script_name:
            # Only a name is given. Search in the default directory
            script_path = src.find_file_in_lpath(script_name,
                                                 config.PATHS.PRODUCTPATH,
                                                 "compil_scripts")
            if not script_path:
                raise src.SatException(
                    _("Compilation script not found: %s") % script_name)
            prod_info.compil_script = script_path
            if src.architecture.is_windows():
                prod_info.compil_script = prod_info.compil_script[:-len(".sh")] + ".bat"
       
        # Check that the script is executable
        if not os.access(prod_info.compil_script, os.X_OK):
            #raise src.SatException(
            #        _("Compilation script cannot be executed: %s") % 
            #        prod_info.compil_script)
            DBG.tofix("Compilation script cannot be executed:", prod_info.compil_script)
    
    # Get the full paths of all the patches
    if product_has_patches(prod_info):
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
    if product_has_env_script(prod_info):
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
    
    if with_install_dir: 
        # The variable with_install_dir is at false only for internal use 
        # of the function get_install_dir
        
        # Save the install_dir key if there is any
        if "install_dir" in prod_info and not "install_dir_save" in prod_info:
            prod_info.install_dir_save = prod_info.install_dir
        
        # if it is not the first time the install_dir is computed, it means
        # that install_dir_save exists and it has to be taken into account.
        if "install_dir_save" in prod_info:
            prod_info.install_dir = prod_info.install_dir_save
        
        # Set the install_dir key
        prod_info.install_dir = get_install_dir(config, base, version, prod_info)
                
    return prod_info

def get_product_section(config, product_name, version, section=None):
    '''Get the product description from the configuration
    
    :param config Config: The global configuration
    :param product_name str: The product name
    :param version str: The version of the product
    :param section str: The searched section (if not None, the section is 
                        explicitly given
    :return: The product description
    :rtype: Config
    '''

    # if section is not None, try to get the corresponding section
    if section:
        if section not in config.PRODUCTS[product_name]:
            return None
        # returns specific information for the given version
        prod_info = config.PRODUCTS[product_name][section]
        prod_info.section = section
        prod_info.from_file = config.PRODUCTS[product_name].from_file
        return prod_info

    # If it exists, get the information of the product_version
    if "version_" + version in config.PRODUCTS[product_name]:
        # returns specific information for the given version
        prod_info = config.PRODUCTS[product_name]["version_" + version]
        prod_info.section = "version_" + version
        prod_info.from_file = config.PRODUCTS[product_name].from_file
        return prod_info
    
    # Else, check if there is a description for multiple versions
    l_section_name = config.PRODUCTS[product_name].keys()
    l_section_ranges = [section_name for section_name in l_section_name 
                        if VERSION_DELIMITER in section_name]
    for section_range in l_section_ranges:
        minimum, maximum = section_range.split(VERSION_DELIMITER)
        if (src.only_numbers(version) >= src.only_numbers(minimum)
                    and src.only_numbers(version) <= src.only_numbers(maximum)):
            # returns specific information for the versions
            prod_info = config.PRODUCTS[product_name][section_range]
            prod_info.section = section_range
            prod_info.from_file = config.PRODUCTS[product_name].from_file
            return prod_info
    
    # Else, get the standard informations
    if "default" in config.PRODUCTS[product_name]:
        # returns the generic information (given version not found)
        prod_info = config.PRODUCTS[product_name].default
        prod_info.section = "default"
        prod_info.from_file = config.PRODUCTS[product_name].from_file
        return prod_info
    
    # if noting was found, return None
    return None
    
def get_install_dir(config, base, version, prod_info):
    '''Compute the installation directory of a given product 
    
    :param config Config: The global configuration
    :param base str: This corresponds to the value given by user in its 
                     application.pyconf for the specific product. If "yes", the
                    user wants the product to be in base. If "no", he wants the
                    product to be in the application workdir
    :param version str: The version of the product
    :param product_info Config: The configuration specific to 
                               the product
    
    :return: The path of the product installation
    :rtype: str
    '''
    install_dir = ""
    in_base = False
    if (("install_dir" in prod_info and prod_info.install_dir == "base") 
                                                            or base == "yes"):
        in_base = True
    if (base == "no" or ("no_base" in config.APPLICATION 
                         and config.APPLICATION.no_base == "yes")):
        in_base = False
    
    if in_base:
        install_dir = get_base_install_dir(config, prod_info, version)
    else:
        if "install_dir" not in prod_info or prod_info.install_dir == "base":
            # Set it to the default value (in application directory)
            install_dir = os.path.join(config.APPLICATION.workdir,
                                                "INSTALL",
                                                prod_info.name)
        else:
            install_dir = prod_info.install_dir

    return install_dir

def get_base_install_dir(config, prod_info, version):
    '''Compute the installation directory of a product in base 
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product
    :param version str: The version of the product    
    :return: The path of the product installation
    :rtype: str
    '''    
    base_path = src.get_base_path(config) 
    prod_dir = os.path.join(base_path, prod_info.name + "-" + version)
    if not os.path.exists(prod_dir):
        return os.path.join(prod_dir, "config-1")
    
    exists, install_dir = check_config_exists(config, prod_dir, prod_info)
    if exists:
        return install_dir
    
    # Find the first config-<i> directory that is available in the product
    # directory
    found = False 
    label = 1
    while not found:
        install_dir = os.path.join(prod_dir, "config-%i" % label)
        if os.path.exists(install_dir):
            label+=1
        else:
            found = True
            
    return install_dir

def check_config_exists(config, prod_dir, prod_info):
    '''Verify that the installation directory of a product in a base exists
       Check all the config-<i> directory and verify the sat-config.pyconf file
       that is in it 
    
    :param config Config: The global configuration
    :param prod_dir str: The product installation directory path 
                         (without config-<i>)
    :param product_info Config: The configuration specific to 
                               the product
    :return: True or false is the installation is found or not 
             and if it is found, the path of the found installation
    :rtype: (boolean, str)
    '''   
    # check if the directories or files of the directory corresponds to the 
    # directory installation of the product
    l_dir_and_files = os.listdir(prod_dir)
    for dir_or_file in l_dir_and_files:
        oExpr = re.compile(config_expression)
        if not(oExpr.search(dir_or_file)):
            # not config-<i>, not interesting
            continue
        # check if there is the file sat-config.pyconf file in the installation
        # directory    
        config_file = os.path.join(prod_dir, dir_or_file, src.CONFIG_FILENAME)
        if not os.path.exists(config_file):
            continue
        
        # If there is no dependency, it is the right path
        if len(prod_info.depend)==0:
            compile_cfg = src.pyconf.Config(config_file)
            if len(compile_cfg) == 0:
                return True, os.path.join(prod_dir, dir_or_file)
            continue
        
        # check if there is the config described in the file corresponds the 
        # dependencies of the product
        config_corresponds = True    
        compile_cfg = src.pyconf.Config(config_file)
        for prod_dep in prod_info.depend:
            # if the dependency is not in the config, 
            # the config does not correspond
            if prod_dep not in compile_cfg:
                config_corresponds = False
                break
            else:
                prod_dep_info = get_product_config(config, prod_dep, False)
                # If the version of the dependency does not correspond, 
                # the config does not correspond
                if prod_dep_info.version != compile_cfg[prod_dep]:
                    config_corresponds = False
                    break
        
        for prod_name in compile_cfg:
            if prod_name not in prod_info.depend:
                config_corresponds = False
                break
        
        if config_corresponds:
            return True, os.path.join(prod_dir, dir_or_file)
    
    return False, None
            
            
    
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
        if prod == product_info.name:
            continue
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
    if not product_compiles(product_info):
        return True
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

def check_source(product_info):
    '''Verify if a sources of product is preset. Checks source directory presence
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if it is well installed
    :rtype: boolean
    '''
    DBG.write("check_source product_info", product_info)
    source_dir = product_info.source_dir
    if not os.path.exists(source_dir):
        return False
    if ("present_files" in product_info and 
        "source" in product_info.present_files):
        for file_relative_path in product_info.present_files.source:
            file_path = os.path.join(source_dir, file_relative_path)
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
    '''Know if a product is a SALOME module
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a SALOME module, else False
    :rtype: boolean
    '''
    return ("properties" in product_info and
            "is_SALOME_module" in product_info.properties and
            product_info.properties.is_SALOME_module == "yes")

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

def product_is_vcs(product_info):
    '''Know if a product is download using git, svn or cvs (not archive)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is vcs, else False
    :rtype: boolean
    '''
    return product_info.get_source in AVAILABLE_VCS

def product_is_smesh_plugin(product_info):
    '''Know if a product is a SMESH plugin
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a SMESH plugin, else False
    :rtype: boolean
    '''
    return ("properties" in product_info and
            "smesh_plugin" in product_info.properties and
            product_info.properties.smesh_plugin == "yes")

def product_is_cpp(product_info):
    '''Know if a product is cpp
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a cpp, else False
    :rtype: boolean
    '''
    return ("properties" in product_info and
            "cpp" in product_info.properties and
            product_info.properties.cpp == "yes")

def product_compiles(product_info):
    '''Know if a product compiles or not (some products do not have a 
       compilation procedure)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product compiles, else False
    :rtype: boolean
    '''
    return not("properties" in product_info and
            "compilation" in product_info.properties and
            product_info.properties.compilation == "no")

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

def product_has_env_script(product_info):
    '''Know if a product has an environment script
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product it has an environment script, else False
    :rtype: boolean
    '''
    return "environ" in product_info and "env_script" in product_info.environ

def product_has_patches(product_info):
    '''Know if a product has one or more patches
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has one or more patches
    :rtype: boolean
    '''
    return "patches" in product_info and len(product_info.patches) > 0

def product_has_logo(product_info):
    '''Know if a product has a logo (YACSGEN generate)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: The path of the logo if the product has a logo, else False
    :rtype: Str
    '''
    if ("properties" in product_info and
            "logo" in product_info.properties):
        return product_info.properties.logo
    else:
        return False

def product_has_salome_gui(product_info):
    '''Know if a product has a SALOME gui
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has a SALOME gui, else False
    :rtype: Boolean
    '''
    return ("properties" in product_info and
            "has_salome_gui" in product_info.properties and
            product_info.properties.has_salome_gui == "yes")

def product_is_mpi(product_info):
    '''Know if a product has openmpi in its dependencies
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has openmpi inits dependencies
    :rtype: boolean
    '''
    return "openmpi" in product_info.depend

def product_is_generated(product_info):
    '''Know if a product is generated (YACSGEN)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is generated
    :rtype: boolean
    '''
    return ("properties" in product_info and
            "generate" in product_info.properties and
            product_info.properties.generate == "yes")

def get_product_components(product_info):
    '''Get the component list to generate with the product
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: The list of names of the components
    :rtype: List
    
    '''
    if not product_is_generated(product_info):
        return []
    
    compo_list = []
    if "component_name" in product_info:
        compo_list = product_info.component_name
    
        if isinstance(compo_list, str):
            compo_list = [ compo_list ]

    return compo_list
