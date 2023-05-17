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

"""\
In this file are implemented the methods 
relative to the product notion of salomeTools
"""

import os
import re
import pprint as PP

import src
import src.debug as DBG
import src.versionMinorMajorPatch as VMMP

AVAILABLE_VCS = ['git', 'svn', 'cvs']

CONFIG_FILENAME = "sat-config-" # trace product depends version(s)
PRODUCT_FILENAME = "sat-product-" # trace product compile config
config_expression = "^config-\d+$"

def get_product_config(config, product_name, with_install_dir=True):
    """Get the specific configuration of a product from the global configuration
    
    :param config Config: The global configuration
    :param product_name str: The name of the product
    :param with_install_dir boolean: If false, do not provide an install 
                                     directory (at false only for internal use 
                                     of the function check_config_exists)
    :return: the specific configuration of the product
    :rtype: Config
    """

    # Get the version of the product from the application definition
    version = config.APPLICATION.products[product_name]
    
    # Define debug and dev modes
    # Get the tag if a dictionary is given in APPLICATION.products for the
    # current product 
    debug = 'no'
    dev = 'no'
    hpc = 'no'
    verbose = 'no'
    base = 'maybe'
    section = None

    # if no version, then take the default one defined in the application
    if isinstance(version, bool) or isinstance(version, str): 
        # in this case tag is mandatory, not debug, verbose, dev
        if 'debug' in config.APPLICATION:
            debug = config.APPLICATION.debug
        if 'verbose' in config.APPLICATION:
            verbose = config.APPLICATION.verbose
        if 'dev' in config.APPLICATION:
            dev = config.APPLICATION.dev
        if 'hpc' in config.APPLICATION:
            hpc = config.APPLICATION.hpc
        if 'base' in config.APPLICATION:
            base = config.APPLICATION.base

    # special case for which only the product name is mentionned 
    if isinstance(version, bool):
        version = config.APPLICATION.tag

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
        elif 'debug' in config.APPLICATION:
            debug = config.APPLICATION.debug
        
        # Get the verbose if any
        if 'verbose' in dic_version:
            verbose = dic_version.verbose
        elif 'verbose' in config.APPLICATION:
            verbose = config.APPLICATION.verbose
        
        # Get the dev if any
        if 'dev' in dic_version:
            dev = dic_version.dev
        elif 'dev' in config.APPLICATION:
            dev = config.APPLICATION.dev
        
        # Get the hpc if any
        if 'hpc' in dic_version:
            hpc = dic_version.hpc
        elif 'hpc' in config.APPLICATION:
            hpc = config.APPLICATION.hpc

        # Get the base if any
        if 'base' in dic_version:
            base = dic_version.base
        elif 'base' in config.APPLICATION:
            base = config.APPLICATION.base

        # Get the section if any
        if 'section' in dic_version:
            section = dic_version.section
    
    # this case occur when version is overwritten, cf sat # 8897
    if isinstance(version, dict): 
        dic_version = version
        # Get the version/tag
        if not 'tag' in dic_version:
            version = config.APPLICATION.tag
        else:
            version = dic_version["tag"]
        
        # Get the debug if any
        if 'debug' in dic_version:
            debug = dic_version["debug"]
        elif 'debug' in config.APPLICATION:
            debug = config.APPLICATION.debug
        
        # Get the verbose if any
        if 'verbose' in dic_version:
            verbose = dic_version["verbose"]
        elif 'verbose' in config.APPLICATION:
            verbose = config.APPLICATION.verbose
        
        # Get the dev if any
        if 'dev' in dic_version:
            dev = dic_version["dev"]
        elif 'dev' in config.APPLICATION:
            dev = config.APPLICATION.dev
        
        # Get the hpc if any
        if 'hpc' in dic_version:
            hpc = dic_version['hpc']
        elif 'hpc' in config.APPLICATION:
            hpc = config.APPLICATION.hpc

        # Get the base if any
        if 'base' in dic_version:
            base = dic_version["base"]

        # Get the section if any
        if 'section' in dic_version:
            section = dic_version['section']

    vv = version
    # substitute some character with _ in order to get the correct definition
    # in config.PRODUCTS. This is done because the pyconf tool does not handle
    # the . and - characters 
    for c in ".-/": vv = vv.replace(c, "_")

    prod_info = None
    if product_name in config.PRODUCTS:
        # Search for the product description in the configuration
        prod_info = get_product_section(config, product_name, vv, section)
        
        # get salomeTool version
        prod_info.sat_version = src.get_salometool_version(config)

        # merge opt_depend in depend
        if prod_info is not None and 'opt_depend' in prod_info:
            for depend in prod_info.opt_depend:
                if (depend in config.APPLICATION.products) and (depend not in prod_info.depend) :
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
        if prod_info is not None and \
           (os.path.isdir(version) or version.startswith("/")):
           # we consider a (fixed) path  existing paths; 
           # or paths starting with '/' (the objective is to print a correct 
           # message to the user in case of non existing path.)
            prod_info.install_dir = version
            prod_info.get_source = "fixed"
            prod_info.install_mode = "fixed"
        
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
Please create a %(1)s.pyconf file somewhere in:
  %(2)s""") % {
  "1": product_name,
  "2": PP.pformat(config.PATHS.PRODUCTPATH) }
        else:
            msg = _("""\
No definition corresponding to the version %(1)s was found in the file:
  %(2)s.
Please add a section in it.""") % {"1" : vv, "2" : prod_pyconf_path}
        raise src.SatException(msg)
    
    # Set the debug, dev and version keys
    prod_info.debug = debug
    prod_info.verbose = verbose
    prod_info.dev = dev
    prod_info.hpc = hpc
    prod_info.version = version
    if base != 'maybe':
        prod_info.base = base

    # Set the archive_info if the product is get in archive mode
    if prod_info.get_source == "archive":
        if not "archive_info" in prod_info:
            prod_info.addMapping("archive_info",
                                 src.pyconf.Mapping(prod_info),
                                 "")
        if "archive_name" in prod_info.archive_info: 
            arch_name = prod_info.archive_info.archive_name
        elif "archive_prefix" in prod_info.archive_info:
            arch_name = prod_info.archive_info.archive_prefix + "-" + version + ".tar.gz"
        else:
            # standard name
            arch_name = product_name + "-" + version + ".tar.gz"

        arch_path = src.find_file_in_lpath(arch_name,
                                           config.PATHS.ARCHIVEPATH)
        if not arch_path:
            # arch_path is not found. It may generate an error in sat source,
            #                         unless the archive is found in ftp serveur
            prod_info.archive_info.archive_name = arch_name #without path
        else:
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
        
        # Get the path of the script file
        # if windows supposed '.bat', if linux supposed '.sh'
        # but user set extension script file in his pyconf as he wants, no obligation.
        script = prod_info.compil_script
        script_name = os.path.basename(script)
        if script == script_name:
            # Only a name is given. Search in the default directory
            script_path = src.find_file_in_lpath(script_name, config.PATHS.PRODUCTPATH, "compil_scripts")
            if not script_path:
                msg = _("Compilation script %s not found in") % script_name
                DBG.tofix(msg, config.PATHS.PRODUCTPATH, True) # say where searched
                script_path = "%s_(Not_Found_by_Sat!!)" % script_name
            prod_info.compil_script = script_path

       
        # Check that the script is executable
        if os.path.exists(prod_info.compil_script) and not os.access(prod_info.compil_script, os.X_OK):
            DBG.tofix("Compilation script  file is not in 'execute mode'", prod_info.compil_script, True)
    
    # If the product has a post install script, check the script existence
    # and if it is executable
    if product_has_post_script(prod_info):
        # Check the compil_script key existence
        
        # Get the path of the script file
        # if windows supposed '.bat', if linux supposed '.sh'
        # but user set extension script file in his pyconf as he wants, no obligation.
        script = prod_info.post_script
        script_name = os.path.basename(script)
        if script == script_name:
            # Only a name is given. Search in the default directory
            script_path = src.find_file_in_lpath(script_name, config.PATHS.PRODUCTPATH, "post_scripts")
            if not script_path:
                msg = _("Post install script %s not found in") % script_name
                DBG.tofix(msg, config.PATHS.PRODUCTPATH, True) # say where searched
                script_path = "%s_(Not_Found_by_Sat!!)" % script_name
            prod_info.post_script = script_path

       
        # Check that the script is executable
        if os.path.exists(prod_info.post_script) and not os.access(prod_info.post_script, os.X_OK):
            DBG.tofix("Post install script file is not in 'execute mode'", prod_info.post_script, True)

    # Get the full paths of all the patches
    if product_has_patches(prod_info):
        patches = []
        try:
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
        except:
          DBG.tofix("problem in prod_info.patches", prod_info)
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
        prod_info.install_dir,prod_info.install_mode = get_install_dir(config, version, prod_info)
                
    return prod_info

def get_product_section(config, product_name, version, section=None):
    """Build the product description from the configuration
    
    :param config Config: The global configuration
    :param product_name str: The product name
    :param version str: The version of the product as 'V8_4_0', or else.
    :param section str: The searched section (if not None, the section is 
                        explicitly given
    :return: The product description
    :rtype: Config
    """


    #get product definition and determine if the incremental definition mode is activated
    aProd = config.PRODUCTS[product_name]
    if "default" in aProd and\
       "properties" in aProd.default and\
       "incremental" in aProd.default.properties and\
       aProd.default.properties.incremental == "yes":
        # in this (new) mode the definition of the product is given by the default section
        # and is incremented by others.
        is_incr=True
    else:
        # in this (historic) mode the definition of the product is given by a full unique section
        is_incr=False

    # decode version number
    try:
      versionMMP = VMMP.MinorMajorPatch(version)
    except: # example setuptools raise "minor in major_minor_patch is not integer: '0_6c11'"
      versionMMP = None

    # if a section is explicitely specified we select it
    if section:
        if section not in aProd:
            pi=None
        # returns specific information for the given version
        pi = aProd[section]
        pi.section = section
        pi.from_file = aProd.from_file

    # If it exists, get the information of the product_version
    # ex: 'version_V6_6_0' as salome version classical syntax
    elif "version_" + version in aProd:
        # returns specific information for the given version
        pi = aProd["version_" + version]
        pi.section = "version_" + version
        pi.from_file = aProd.from_file

    # Else, check if there is a description for multiple versions
    else:
        l_section_names = aProd.keys()
        l_section_ranges = []
        tagged = []
        for name in l_section_names:
          aRange = VMMP.getRange_majorMinorPatch(name)
          if aRange is not None:
            l_section_ranges.append((name, aRange))

        if versionMMP is not None and len(l_section_ranges) > 0:
          for name, (vmin, vmax) in l_section_ranges:
            if versionMMP >= vmin and versionMMP <= vmax:
              tagged.append((name, [vmin, vmax]))

        if len(tagged) > 1:
          DBG.write("multiple version ranges tagged for '%s', fix it" % version,
                         PP.pformat(tagged))
          pi=None
        elif len(tagged) == 1: # ok
          name, (vmin, vmax) = tagged[0]
          pi = aProd[name]
          pi.section = name
          pi.from_file = aProd.from_file

        # Else, get the standard informations
        elif "default" in aProd:
            # returns the generic information (given version not found)
            pi = aProd.default
            pi.section = "default"
            pi.from_file = aProd.from_file
        else:
            pi=None

    if is_incr:
        # If the definition is incremental, we take the default section
        # and then complete it with other sections : 
        #   - default_win
        #   - the selected section (pi)
        #   - the selected _win section
        prod_info=aProd["default"]
        prod_info.from_file = aProd.from_file
        prod_info.section = "default"
        if src.architecture.is_windows() and "default_win" in aProd:
            for key in aProd["default_win"]:
                prod_info[key]=aProd["default_win"][key]
        if pi!=None and pi.section!="default":
            # update prod_info with incremental definition contained in pi
            for key in pi:
                prod_info[key]=pi[key]
            win_section=pi.section+"_win"
            if src.architecture.is_windows() and win_section in aProd:
                for key in aProd[win_section]:
                    prod_info[key]=aProd[win_section][key]
    else:
        prod_info=pi

    #DBG.write("product info returned for product %s with version %s and section %s" %\
    #          (product_name, version, section), prod_info)
    return prod_info
    
def get_install_dir(config, version, prod_info):
    """Compute the installation directory of a given product 
    
    :param config Config: The global configuration
    :param base str: This corresponds to the value given by user in its 
                     application.pyconf for the specific product. If "yes", the
                     user wants the product to be in base. If "no", he wants the
                     product to be in the application workdir
    :param version str: The version of the product
    :param product_info Config: The configuration specific to 
                               the product
    
    :return: The path of the product installation and the mode of the install directory (base/implicit/fixed/value)
    :rtype: str,str
    """
    install_dir = ""
    in_base = False
    
    # prod_info.base : corresponds to what is specified in application pyconf (either from the global key base, or from a product dict)
    # prod_info.install_dir : corresponds to what is specified in product pyconf (usually "base" for prerequisites)
    if ( ("install_dir" in prod_info and prod_info.install_dir == "base") # product is declared as base in its own config 
                                      or ("base" in prod_info  and prod_info.base != "no") ):  # product is declared as base in the application
        # a product goes in base if install_dir is set to base, or if product was declared based in application pyconf
        in_base = True

    # check desactivation of base at application level
    if ( "base" in prod_info  and prod_info.base == "no"):
        in_base = False

    if in_base:
        install_dir = get_base_install_dir(config, prod_info, version)
        install_mode = "base"
    else:
        if ("install_mode" in prod_info and prod_info.install_mode in ["implicit", "base"]) or\
           ("install_dir" not in prod_info or prod_info.install_dir == "base"):
            # the check to "base" comes from the package case were base mode is changed dynamically 
            # to create a package launcher.

            # Set it to the default value (in application directory)
            install_mode = "implicit"
            if ( src.appli_test_property(config,"single_install_dir", "yes") and 
                 src.product.product_test_property(prod_info,"single_install_dir", "yes")):
                # when single_install_dir mode is activated in tha application
                # we use config.INTERNAL.config.single_install_dir for products 
                # having single_install_dir property
                install_dir = os.path.join(config.APPLICATION.workdir,
                                           config.INTERNAL.config.install_dir,
                                           config.INTERNAL.config.single_install_dir)
            elif ( src.appli_test_property(config,"pip", "yes") and 
                   src.product.product_test_property(prod_info,"pip", "yes") and
                   src.appli_test_property(config,"pip_install_dir", "python") ):
                # when pip mode is activated in the application
                # and product is pip, and pip_install_dir is set to python 
                # we assume python in installed in install_dir/Python
                install_dir = os.path.join(config.APPLICATION.workdir,
                                           config.INTERNAL.config.install_dir,
                                           "Python")   
            else:
                install_dir = os.path.join(config.APPLICATION.workdir,
                                           config.INTERNAL.config.install_dir,
                                           prod_info.name)
        else:
            install_dir = prod_info.install_dir
            install_mode = "value"

    return install_dir,install_mode

def get_base_install_dir(config, prod_info, version):
    """Compute the installation directory of a product in base 
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product
    :param version str: The version of the product    
    :param base str: This corresponds to the value given by user in its 
                     application.pyconf for the specific product. If "yes", the
                     user wants the product to be in base. If "no", he wants the
                     product to be in the application workdir.
                     if it contains something else, is is interpreted as the name 
                     of a base we build for module load.
    :return: The path of the product installation
    :rtype: str
    """    
    
    # get rid of / to avoid create subdirectories cf sat #18546
    version_wslash=version.replace("/", "_") 

    if ( src.appli_test_property(config,"pip", "yes") and 
         src.product.product_test_property(prod_info,"pip", "yes") and
         src.appli_test_property(config,"pip_install_dir", "python") ):
         # when pip mode is activated in the application
         # and product is pip, and pip_install_dir is set to python 
        python_info=get_product_config(config, "Python")
        return python_info.install_dir

    base_path = src.get_base_path(config) 
    if "base" in prod_info and prod_info.base != "no" and prod_info.base != "yes":
        # we are in the case of a named base
        prod_dir = os.path.join(base_path, "apps", prod_info.base, prod_info.name, version_wslash)
        return prod_dir
    
    prod_dir = os.path.join(base_path, prod_info.name + "-" + version_wslash)
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

def add_compile_config_file(p_info, config):
    '''Execute the proper configuration command(s)
       in the product build directory.

    :param p_info Config: The specific config of the product
    :param config Config: The global configuration
    '''
    # Create the compile config
    # DBG.write("add_compile_config_file", p_info, True)
    res = src.pyconf.Config()
    res.addMapping(p_info.name, src.pyconf.Mapping(res), "")
    res[p_info.name]= p_info.version

    depprod=[]
    for d in p_info.depend:
        depprod.append(d)
    if "build_depend" in p_info:
        for d in p_info.build_depend:
            depprod.append(d)
    for prod_name in depprod:
      if prod_name not in res:
        res.addMapping(prod_name, src.pyconf.Mapping(res), "")
      prod_dep_info = src.product.get_product_config(config, prod_name, False)
      res[prod_name] = prod_dep_info.version
    # Write it in the install directory of the product
    # This file is for automatic reading/checking
    # see check_config_exists method
    afilename = CONFIG_FILENAME + p_info.name + ".pyconf"
    aFile = os.path.join(p_info.install_dir, afilename)
    with open(aFile, 'w') as f:
      res.__save__(f)

    # this file is not mandatory, is for human eye reading
    afilename = PRODUCT_FILENAME + p_info.name + ".pyconf"
    aFile = os.path.join(p_info.install_dir, afilename)
    try:
      with open(aFile, 'w') as f:
        p_info.__save__(f, evaluated=True) # evaluated expressions mode
    except:
      # sometime some information cannot be evaluated.
      # for example, in the context of non VCS archives, information on git server is not available.
      DBG.write("Warning : sat was not able to evaluate and write down some information in file %s" % aFile)
  

def check_config_exists(config, prod_dir, prod_info, verbose=False):
    """\
    Verify that the installation directory of a product in a base exists.
    Check all the config-<i>/sat-config.py files found for correspondence
    with current config and prod_info depend-version-tags
    
    :param config Config: The global configuration
    :param prod_dir str: The product installation directory path 
                         (without config-<i>)
    :param product_info Config: The configuration specific to 
                               the product
    :return: True or false is the installation is found or not 
             and if it is found, the path of the found installation
    :rtype: (boolean, str)
    """
    # check if the directories or files of the directory corresponds to the
    # directory installation of the product
    if os.path.isdir(prod_dir):
      l_dir_and_files = os.listdir(prod_dir)
    else:
      raise Exception("Inexisting directory '%s'" % prod_dir)

    DBG.write("check_config_exists 000",  (prod_dir, l_dir_and_files), verbose)
    DBG.write("check_config_exists 111",  prod_info, verbose)

    depend_all=[]
    if "depend" in prod_info:
        for d in prod_info.depend:
            depend_all.append(d)
    if "build_depend" in prod_info:
        for d in prod_info.build_depend:
            depend_all.append(d)
    for dir_or_file in l_dir_and_files:
        oExpr = re.compile(config_expression)
        if not(oExpr.search(dir_or_file)):
            # in mode BASE, not config-<i>, not interesting
            # DBG.write("not interesting", dir_or_file, True)
            continue
        # check if there is the file sat-config.pyconf file in the installation
        # directory    
        afilename = CONFIG_FILENAME + prod_info.name + ".pyconf"
        config_file = os.path.join(prod_dir, dir_or_file, afilename)
        DBG.write("check_config_exists 222", config_file, verbose)
        if not os.path.exists(config_file):
            continue
        
        # check if there is the config described in the file corresponds the 
        # dependencies of the product
        config_corresponds = True    
        compile_cfg = src.pyconf.Config(config_file)
        for prod_dep in depend_all:
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

        if config_corresponds:
          for prod_name in compile_cfg:
            # assume new compatibility with prod_name in sat-config.pyconf files
            if prod_name == prod_info.name:
              if prod_info.version == compile_cfg[prod_name]:
                DBG.write("check_config_exists OK 333", compile_cfg, verbose)
                pass
              else: # no correspondence with newer with prod_name sat-config.pyconf files
                config_corresponds = False
                break
            else:
              # as old compatibility without prod_name sat-config.pyconf files
              if prod_name not in depend_all:
                # here there is an unexpected depend in an old compilation
                config_corresponds = False
                break
        
        if config_corresponds: # returns (and stops) at first correspondence found
            DBG.write("check_config_exists OK 444", dir_or_file, verbose)
            return True, os.path.join(prod_dir, dir_or_file)

    # no correspondence found
    return False, None
            
            
    
def get_products_infos(lproducts, config):
    """Get the specific configuration of a list of products
    
    :param lproducts List: The list of product names
    :param config Config: The global configuration
    :return: the list of tuples 
             (product name, specific configuration of the product)
    :rtype: [(str, Config)]
    """
    products_infos = []
    # Loop on product names
    for prod in lproducts:       
        # Get the specific configuration of the product
        prod_info = get_product_config(config, prod)
        if prod_info is not None:
            products_infos.append((prod, prod_info))
        else:
            msg = _("The %s product has no definition in the configuration.") % prod
            raise src.SatException(msg)
    return products_infos


def get_products_list(options, cfg, logger):
    """
    method that gives the product list with their informations from
    configuration regarding the passed options.

    :param options Options: The Options instance that stores the commands arguments
    :param cfg Config: The global configuration
    :param logger Logger: The logger instance to use for the display and logging
    :return: The list of (product name, product_informations).
    :rtype: List
    """
    # Get the products to be prepared, regarding the options
    if options.products is None:
        # No options, get all products sources
        products = cfg.APPLICATION.products
    else:
        # if option --products, check that all products of the command line
        # are present in the application.
        """products = options.products
        for p in products:
            if p not in cfg.APPLICATION.products:
                raise src.SatException(_("Product %(product)s "
                            "not defined in application %(application)s") %
                        { 'product': p, 'application': cfg.VARS.application} )"""

        products = src.getProductNames(cfg, options.products, logger)

    # Construct the list of tuple containing
    # the products name and their definition
    resAll = src.product.get_products_infos(products, cfg)

    # if the property option was passed, filter the list
    if options.properties: # existing properties
      ok = []
      ko = []
      res =[]
      prop, value = options.properties # for example 'is_SALOME_module', 'yes'
      if value[0] == '!':
          for p_name, p_info in resAll:
            try:
              if p_info.properties[prop] == value[1:]:
                ko.append(p_name)
              else:
                res.append((p_name, p_info))
                ok.append(p_name)
            except:
              res.append((p_name, p_info))
              ok.append(p_name)
      else:
          for p_name, p_info in resAll:
            try:
              if p_info.properties[prop] == value:
                res.append((p_name, p_info))
                ok.append(p_name)
              else:
                ko.append(p_name)
            except:
              ko.append(p_name)

      if len(ok) != len(resAll):
        logger.trace("on properties %s\n products accepted:\n %s\n products rejected:\n %s\n" %
                       (options.properties, PP.pformat(sorted(ok)), PP.pformat(sorted(ko))))
      else:
        logger.warning("properties %s\n seems useless with no products rejected" %
                       (options.properties))
    else:
      res = resAll # not existing properties as all accepted

    return res


def get_product_dependencies(config, product_name, product_info):
    """\
    Get the list of products that are 
    in the product_info dependencies
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product
    :return: the list of products in dependence
    :rtype: list
    """
    from compile import get_dependencies_graph, depth_search_graph
    all_products_infos = get_products_infos(
                             config.APPLICATION.products,
                             config)
    all_products_graph=get_dependencies_graph(all_products_infos)
    res=[]
    res=depth_search_graph(all_products_graph, product_name, res)
    return res[1:]  # remove the product himself (in first position)

def check_installation(config, product_info):
    """\
    Verify if a product is well installed. Checks install directory presence
    and some additional files if it is defined in the config 
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if it is well installed
    :rtype: boolean
    """
    # don't check products that are not compiled
    if not product_compiles(product_info):
        return True

    if product_is_native(product_info):
        # check a system product
        check_cmd=src.system.get_pkg_check_cmd(config.VARS.dist_name)
        run_pkg,build_pkg=src.product.check_system_dep(config.VARS.dist, check_cmd, product_info)
        build_dep_ko=[]
        for pkg in build_pkg:
            if "KO" in build_pkg[pkg]:
               build_dep_ko.append(pkg) 
        if build_dep_ko:
              # the product is not installed : display message and return error status
              msg="Please install them with %s before compiling salome" % check_cmd[0]
              print("\nmissing compile time dependencies : ")
              for md in build_dep_ko: 
                  print(md)
              print(msg)
              return False
        else:
            return True    

    install_dir = product_info.install_dir
    if src.product.product_is_fixed(product_info):
        # we check directly the install dir only for fixed products
        # (there is no pyconf file in that case)
        if not os.path.exists(install_dir):
            return False
    else:
        filename = CONFIG_FILENAME + product_info.name + ".pyconf"
        if not os.path.exists(os.path.join(install_dir, filename)): 
            return False

    # check extra files if specified in present_files.install section
    if ("present_files" in product_info and 
        "install" in product_info.present_files):
        for file_relative_path in product_info.present_files.install:
            file_path = os.path.join(install_dir, file_relative_path)
            if not os.path.exists(file_path):
                return False
    return True

def check_source(product_info):
    """Verify if a sources of product is preset. Checks source directory presence
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if it is well installed
    :rtype: boolean
    """
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

def product_is_salome(product_info):
    """Know if a product is a SALOME module
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a SALOME module, else False
    :rtype: boolean
    """
    return ("properties" in product_info and
            "is_SALOME_module" in product_info.properties and
            product_info.properties.is_SALOME_module == "yes")

def product_is_configuration(product_info):
    """Know if a product is a configuration module
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a configuration module, else False
    :rtype: boolean
    """
    return ("properties" in product_info and
            "configure_dependency" in product_info.properties and
            product_info.properties.configure_dependency == "yes")

def product_is_fixed(product_info):
    """Know if a product is fixed
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is fixed, else False
    :rtype: boolean
    """
    get_src = product_info.get_source
    return get_src.lower() == 'fixed'

def product_is_native(product_info):
    """Know if a product is native
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is native, else False
    :rtype: boolean
    """
    get_src = product_info.get_source
    return get_src.lower() == 'native'

def product_is_dev(product_info):
    """Know if a product is in dev mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in dev mode, else False
    :rtype: boolean
    """
    dev = product_info.dev
    res = (dev.lower() == 'yes')
    DBG.write('product_is_dev %s' % product_info.name, res)
    # if product_info.name == "XDATA": return True #test #10569
    return res

def product_is_hpc(product_info):
    """Know if a product is in hpc mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in hpc mode, else False
    :rtype: boolean
    """
    hpc = product_info.hpc
    res = (hpc.lower() == 'yes')
    return res

def product_is_debug(product_info):
    """Know if a product is in debug mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in debug mode, else False
    :rtype: boolean
    """
    debug = product_info.debug
    return debug.lower() == 'yes'

def product_is_verbose(product_info):
    """Know if a product is in verbose mode
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is in verbose mode, else False
    :rtype: boolean
    """
    verbose = product_info.verbose
    return verbose.lower() == 'yes'

def product_is_autotools(product_info):
    """Know if a product is compiled using the autotools
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is autotools, else False
    :rtype: boolean
    """
    build_src = product_info.build_source
    return build_src.lower() == 'autotools'

def product_is_cmake(product_info):
    """Know if a product is compiled using the cmake
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is cmake, else False
    :rtype: boolean
    """
    build_src = product_info.build_source
    return build_src.lower() == 'cmake'

def product_is_vcs(product_info):
    """Know if a product is download using git, svn or cvs (not archive)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is vcs, else False
    :rtype: boolean
    """
    return product_info.get_source in AVAILABLE_VCS

def product_is_smesh_plugin(product_info):
    """Know if a product is a SMESH plugin
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a SMESH plugin, else False
    :rtype: boolean
    """
    return ("properties" in product_info and
            "smesh_plugin" in product_info.properties and
            product_info.properties.smesh_plugin == "yes")

def product_is_cpp(product_info):
    """Know if a product is cpp
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is a cpp, else False
    :rtype: boolean
    """
    return ("properties" in product_info and
            "cpp" in product_info.properties and
            product_info.properties.cpp == "yes")

def product_compiles(product_info):
    """\
    Know if a product compiles or not 
    (some products do not have a compilation procedure)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product compiles, else False
    :rtype: boolean
    """
    return not("properties" in product_info and
            "compilation" in product_info.properties and
            product_info.properties.compilation == "no")

def product_has_script(product_info):
    """Know if a product has a compilation script
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product it has a compilation script, else False
    :rtype: boolean
    """
    if "build_source" not in product_info:
        # Native case
        return False
    build_src = product_info.build_source
    return build_src.lower() == 'script'

def product_has_env_script(product_info):
    """Know if a product has an environment script
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product it has an environment script, else False
    :rtype: boolean
    """
    return "environ" in product_info and "env_script" in product_info.environ

def product_has_patches(product_info):
    """Know if a product has one or more patches
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has one or more patches
    :rtype: boolean
    """   
    res = ( "patches" in product_info and len(product_info.patches) > 0 )
    return res

def product_has_post_script(product_info):
    """Know if a product has a post install script
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has one or more patches
    :rtype: boolean
    """   
    res = ( "post_script" in product_info and len(product_info.post_script) > 0 and not src.architecture.is_windows())
    return res

def product_has_logo(product_info):
    """Know if a product has a logo (YACSGEN generate)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: The path of the logo if the product has a logo, else False
    :rtype: Str
    """
    if ("properties" in product_info and
            "logo" in product_info.properties):
        return product_info.properties.logo
    else:
        return False

def product_has_licence(product_info, path):
    """Find out if a product has a licence
    
    :param product_info Config: The configuration specific to the product
    :param path Str: The path where to search for the licence
    :return: The name of the licence file (the complete path if it is found in the path, else the name, else False
    :rtype: Str
    """
    if ("properties" in product_info and
            "licence" in product_info.properties):
        licence_name = product_info.properties.licence
        if len(path) > 0:
            # search for licence_name in path
            # a- consolidate the path into one signe string licence_path
            licence_path=path[0]
            for lpath in path[1:]:
                licence_path=licence_path+":"+lpath
            licence_path_list=licence_path.split(":")
            licence_fullname = src.find_file_in_lpath(licence_name, licence_path_list)
            if licence_fullname:
                return licence_fullname

        # if the search of licence in path failed, we return its name (not the full path) 
        return licence_name

    else:
        return False  # product has no licence

def product_has_salome_gui(product_info):
    """Know if a product has a SALOME gui
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has a SALOME gui, else False
    :rtype: Boolean
    """
    return ("properties" in product_info and
            "has_salome_gui" in product_info.properties and
            product_info.properties.has_salome_gui == "yes")

def product_is_mpi(product_info):
    """Know if a product has openmpi in its dependencies
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has openmpi inits dependencies
    :rtype: boolean
    """
    return "openmpi" in product_info.depend

def product_is_generated(product_info):
    """Know if a product is generated (YACSGEN)
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is generated
    :rtype: boolean
    """
    return ("properties" in product_info and
            "generate" in product_info.properties and
            product_info.properties.generate == "yes")

def product_is_compile_time(product_info):
    """Know if a product is only used at compile time
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is only used at compile time
    :rtype: boolean
    """
    return ("properties" in product_info and
            "compile_time" in product_info.properties and
            product_info.properties.compile_time == "yes")

def product_is_compile_and_runtime(product_info):
    """Know if a product is only used at compile time
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product is only used at compile time
    :rtype: boolean
    """
    return ("properties" in product_info and
            "compile_and_runtime" in product_info.properties and
            product_info.properties.compile_and_runtime == "yes")



def product_test_property(product_info, property_name, property_value):
    """Generic function to test if a product has a property set to a value
    
    :param product_info Config: The configuration specific to 
                               the product
    :param property_name : The name of the property to check
    :param property_value : The value of the property to test
    :return: True if the product has the property and the property is set to property_value
    :rtype: boolean
    """
    # first check if product has the property
    if not ("properties" in product_info and
            property_name in product_info.properties):
        return False
  
    # then check to the property is set to property_value
    eval_expression = 'product_info.properties.%s == "%s"' % (property_name,property_value)
    result = eval(eval_expression)
    return result

def check_system_dep(distrib, check_cmd, product_info):
    """Search for system dependencies, check if installed
    :param dist : The linux ditribution (CO7,DB10...)
    :param check_cmd Config: The command to use for checking (rpm/apt)
    :param product_info Config: The configuration specific to the product
    :rtype: two dictionnaries for runtime and compile time dependencies with text status
    """
    runtime_dep={}
    build_dep={}

    if "system_info" in product_info:

        sysinfo=product_info.system_info
        additional_sysinfo = None

        for key in sysinfo :
            if distrib in key :
                additional_sysinfo = sysinfo[key]

        if check_cmd[0]=="rpm":
            if "rpm" in sysinfo:
                for pkg in sysinfo.rpm:
                    runtime_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
            if "rpm_dev" in sysinfo:
                for pkg in sysinfo.rpm_dev:
                    build_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
            if additional_sysinfo :
                if "rpm" in additional_sysinfo:
                    for pkg in additional_sysinfo.rpm:
                        runtime_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
                if "rpm_dev" in additional_sysinfo:
                    for pkg in additional_sysinfo.rpm_dev:
                        build_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
        if check_cmd[0]=="apt":
            if "apt" in sysinfo:
                for pkg in sysinfo.apt:
                    runtime_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
            if "apt_dev" in sysinfo:
                for pkg in sysinfo.apt_dev:
                    build_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
            if additional_sysinfo :
                if "apt" in additional_sysinfo:
                    for pkg in additional_sysinfo.apt:
                        runtime_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)
                if "apt_dev" in additional_sysinfo:
                    for pkg in additional_sysinfo.apt_dev:
                        build_dep[pkg]=src.system.check_system_pkg(check_cmd,pkg)

    return runtime_dep,build_dep


def get_product_components(product_info):
    """Get the component list to generate with the product
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: The list of names of the components
    :rtype: List
    
    """
    if not product_is_generated(product_info):
        return []
    
    compo_list = []
    if "component_name" in product_info:
        compo_list = product_info.component_name
    
        if isinstance(compo_list, str):
            compo_list = [ compo_list ]

    return compo_list
def product_is_wheel(product_info):
    """ tells whether a product is a wheel
    
    :param product_info Config: The configuration specific to 
                               the product
    :return: True if the product has a wheel, else False
    :rtype: Boolean
    """
    return ("properties" in product_info and
            "is_wheel" in product_info.properties and
            product_info.properties.is_wheel == "yes")

