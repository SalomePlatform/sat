#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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
import subprocess
import string
import sys
import copy

import src
import src.debug as DBG
import pprint as PP


class Environ:
    """\
    Class to manage the environment context
    """
    def __init__(self, environ=None):
        """Initialization. If the environ argument is passed, the environment
           will be add to it, else it is the external environment.
           
        :param environ dict:  
        """
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ

    def __repr__(self):
        """easy non exhaustive quick resume for debug print"""
        return "%s(\n%s\n)" % (self.__class__.__name__, PP.pformat(self.environ))

    def _expandvars(self, value):
        """\
        replace some $VARIABLE into its actual value in the environment
        
        :param value str: the string to be replaced
        :return: the replaced variable
        :rtype: str
        """
        if src.architecture.is_windows():
            delim = "%"
        else:
            delim = "$"
        if delim in value:
            # The string.Template class is a string class 
            # for supporting $-substitutions
            zt = string.Template(value)
            zt.delimiter = delim
            try:
                value = zt.substitute(self.environ)
            except KeyError as exc:
                pass
                #raise src.SatException(_("Missing definition "
                #                         "in environment: %s") % str(exc))
        return value

    def append_value(self, key, value, sep=os.pathsep):
        """\
        append value to key using sep,
        if value contains ":" or ";" then raise error

        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        """
        # check that value so no contain the system separator
        separator=os.pathsep
        if separator in value:
            raise Exception("Environ append key '%s' value '%s' contains forbidden character '%s'" % (key, value, separator))

        # check if the key is already in the environment
        if key in self.environ:
            value_list = self.environ[key].split(sep)
            # Check if the value is already in the key value or not
            if not value in value_list:
                value_list.append(value)
            else:
                value_list.append(value_list.pop(value_list.index(value)))
            self.set(key, sep.join(value_list))
        else:
            self.set(key, value)

    def append(self, key, value, sep=os.pathsep):
        """\
        Same as append_value but the value argument can be a list
        
        :param key str: the environment variable to append
        :param value str or list: the value(s) to append to key
        :param sep str: the separator string
        """
        if isinstance(value, list):
            for v in value:
                self.append_value(key, v, sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=os.pathsep):
        """\
        prepend value to key using sep,
        if value contains ":" or ";" then raise error
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        # check that value so no contain the system separator
        separator=os.pathsep
        if separator in value:
            raise Exception("Environ append key '%s' value '%s' contains forbidden character '%s'" % (key, value, separator))

        # check if the key is already in the environment
        if key in self.environ:
            value_list = self.environ[key].split(sep)
            if not value in value_list:
                value_list.insert(0, value)
            else:
                value_list.insert(0, value_list.pop(value_list.index(value)))
            self.set(key, sep.join(value_list))
        else:
            self.set(key, value)

    def prepend(self, key, value, sep=os.pathsep):
        """\
        Same as prepend_value but the value argument can be a list
        
        :param key str: the environment variable to prepend
        :param value str or list: the value(s) to prepend to key
        :param sep str: the separator string
        """
        if isinstance(value, list):
            for v in reversed(value): # prepend list, first item at last to stay first
                self.prepend_value(key, v, sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        """\
        Check if the key exists in the environment
        
        :param key str: the environment variable to check
        """
        return key in self.environ.keys()

    def set(self, key, value):
        """\
        Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.environ[key] = self._expandvars(value)

    def get(self, key):
        """\
        Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        if key in self.environ:
            return self.environ[key]
        else:
            return ""

    def get_value(self, key):
        """\
        Get the value of the environment variable "key"
        This method is added for API compatibility with FileEnviron class
        
        :param key str: the environment variable
        """
        return self.get(key)



class SalomeEnviron:
    """\
    Class to manage the environment of SALOME.
    """
    def __init__(self,
                 cfg,
                 environ,
                 forBuild=False,
                 for_package=None,
                 enable_simple_env_script = True):
        """\
        Initialization.

        :param cfg Config: the global config
        :param environ Environ: the Environ instance where 
                                to store the environment variables
        :param forBuild bool: If true, it is a launch environment, 
                              else a build one
        :param for_package str: If not None, produce a relative environment 
                                designed for a package. 
        """
        self.environ = environ
        self.cfg = cfg
        self.forBuild = forBuild
        self.for_package = for_package
        self.enable_simple_env_script = enable_simple_env_script
        self.silent = False
        self.has_python = False
        self.__set_sorted_products_list()

    def __repr__(self):
        """easy almost exhaustive quick resume for debug print"""
        res = {
          "environ" : self.environ,
          "forBuild" : self.forBuild,
          "for_package" : self.for_package,
        }
        return "%s(\n%s\n)" % (self.__class__.__name__, PP.pformat(res))

    def __set_sorted_products_list(self):
        all_products_infos = src.product.get_products_infos(
                                 self.cfg.APPLICATION.products,
                                 self.cfg)
        
        from compile import get_dependencies_graph,depth_first_topo_graph
        all_products_graph=get_dependencies_graph(all_products_infos, self.forBuild)
        visited_nodes=[]
        sorted_nodes=[]
        for n in all_products_graph:
            if n not in visited_nodes:
                visited_nodes,sorted_nodes=depth_first_topo_graph(
                                               all_products_graph, 
                                               n, 
                                               visited_nodes,
                                               sorted_nodes)
        self.sorted_product_list=sorted_nodes
        self.all_products_graph=all_products_graph


    def append(self, key, value, sep=os.pathsep):
        """\
        append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        """
        return self.environ.append(key, value, sep)

    def prepend(self, key, value, sep=os.pathsep):
        """\
        prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        return self.environ.prepend(key, value, sep)

    def is_defined(self, key):
        """\
        Check if the key exists in the environment
        
        :param key str: the environment variable to check
        """
        return self.environ.is_defined(key)

    def get(self, key):
        """\
        Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        return self.environ.get(key)

    def get_value(self, key):
        """\
        Get the real value of the environment variable "key"
        This method is added for API compatibility with FileEnviron class
        
        :param key str: the environment variable
        """
        if key in self.environ:
            return self.environ[key]
        else:
            return ""

    def set(self, key, value):
        """\
        Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        # check if value needs to be evaluated
        if value is not None and value.startswith("`") and value.endswith("`"):
            res = subprocess.Popen("echo %s" % value,
                                   shell=True,
                                   stdout=subprocess.PIPE).communicate()
            value = res[0].strip()

        return self.environ.set(key, value)

    def dump(self, out):
        """\
        Write the environment to out
        
        :param out file: the stream where to write the environment
        """
        for k in self.environ.environ.keys():
            try:
                value = self.get(k)
            except:
                value = "?"
            out.write("%s=%s\n" % (k, value))

    def add_line(self, nb_line):
        """\
        Add empty lines to the out stream (in case of file generation)
        
        :param nb_line int: the number of empty lines to add
        """
        if 'add_line' in dir(self.environ):
            self.environ.add_line(nb_line)

    def add_comment(self, comment):
        """\
        Add a commentary to the out stream (in case of file generation)
        
        :param comment str: the commentary to add
        """
        if 'add_comment' in dir(self.environ):
            self.environ.add_comment(comment)

    def add_warning(self, warning):
        """\
        Add a warning to the out stream (in case of file generation)
        
        :param warning str: the warning to add
        """
        if 'add_warning' in dir(self.environ):
            self.environ.add_warning(warning)

    def finish(self):
        """\
        Add a final instruction in the out file (in case of file generation)
        
        :param required bool: Do nothing if required is False
        """
        if 'finish' in dir(self.environ):
            self.environ.add_line(1)
            # what for ?
            # self.environ.add_comment("clean all the path")
            self.environ.finish()

    def set_python_libdirs(self):
        """Set some generic variables for python library paths"""
        ver = self.get('PYTHON_VERSION')
        self.set('PYTHON_LIBDIR', os.path.join('lib',
                                                'python' + ver,
                                                'site-packages'))
        self.python_lib = self.get('PYTHON_LIBDIR')
        self.has_python = True

    def set_application_env(self, logger):
        """\
        Sets the environment defined in the APPLICATION file.
        
        :param logger Logger: The logger instance to display messages
        """
        
        if self.for_package:
           if src.architecture.is_windows():
              self.set("PRODUCT_ROOT_DIR", "%out_dir_Path%")
           else:
              self.set("PRODUCT_ROOT_DIR", "out_dir_Path")

        else:
           self.cfg.APPLICATION.environ.PRODUCT_ROOT_DIR = src.pyconf.Reference(self.cfg, src.pyconf.DOLLAR, "workdir")


        # Set the variables defined in the "environ" section
        if 'environ' in self.cfg.APPLICATION:
            # we write PRODUCT environment it in order to conform to 
            # parseConfigFile.py
            self.add_comment("PRODUCT environment") 
            self.load_cfg_environment(self.cfg.APPLICATION.environ)
            if self.forBuild and "build" in self.cfg.APPLICATION.environ:
                self.load_cfg_environment(self.cfg.APPLICATION.environ.build)
            if not self.forBuild and "launch" in self.cfg.APPLICATION.environ:
                self.load_cfg_environment(self.cfg.APPLICATION.environ.launch)
            self.add_line(1)


    def set_salome_minimal_product_env(self, product_info, logger):
        """\
        Sets the minimal environment for a SALOME product.
        xxx_ROOT_DIR and xxx_SRC_DIR
        
        :param product_info Config: The product description
        :param logger Logger: The logger instance to display messages        
        """
        DBG.write("set_salome_minimal_product_env", product_info)

        # set root dir
        root_dir = product_info.name + "_ROOT_DIR"
        
        if src.product.product_is_configuration(product_info):
            # configuration modules are not installed, root_dir points at source dir
            if not self.for_package:
                self.set(root_dir, product_info.source_dir)
            else:
                self.set(root_dir, os.path.join("out_dir_Path",
                         "SOURCES",
                         os.path.basename(product_info.source_dir)))
        elif 'install_dir' in product_info and product_info.install_dir:
            self.set(root_dir, product_info.install_dir)
        elif not self.silent:
            logger.write("  " + _("No install_dir for product %s\n") %
                          product_info.name, 5)
    
        source_in_package = src.get_property_in_product_cfg(product_info,
                                                           "sources_in_package")
        if not self.for_package or source_in_package == "yes":
            # set source dir, unless no source dir
            if not src.product.product_is_fixed(product_info):
                src_dir = product_info.name + "_SRC_DIR"
                if not self.for_package:
                    self.set(src_dir, product_info.source_dir)
                else:
                    self.set(src_dir, os.path.join("out_dir_Path",
                             "SOURCES",
                             os.path.basename(product_info.source_dir)))

    def expand_salome_modules(self, pi):
        if 'component_name' in pi:
            compo_name = pi.component_name
        else:
            compo_name = pi.name
        self.append('SALOME_MODULES', compo_name, ',')
        
        
    def set_salome_generic_product_env(self, pi):
        """\
        Sets the generic environment for a SALOME product.
        
        :param pi Config: The product description
        """
        if src.product.product_is_configuration(pi):
            # configuration modules are not installed and should not be set like others
            return

        # Construct XXX_ROOT_DIR
        env_root_dir = self.get(pi.name + "_ROOT_DIR")
        l_binpath_libpath = []
        # create additional ROOT_DIR for CPP components
        if 'component_name' in pi:
            compo_name = pi.component_name
            if compo_name + "CPP" == pi.name:
                compo_root_dir = compo_name + "_ROOT_DIR"
                envcompo_root_dir = os.path.join(
                            self.cfg.TOOLS.common.install_root, compo_name )
                self.set(compo_root_dir ,  envcompo_root_dir)
                bin_path = os.path.join(envcompo_root_dir, 'bin', 'salome')
                lib_path = os.path.join(envcompo_root_dir, 'lib', 'salome')
                l_binpath_libpath.append( (bin_path, lib_path) )


        if src.get_property_in_product_cfg(pi, "fhs"):
            lib_path = os.path.join(env_root_dir, 'lib')
            bin_path = os.path.join(env_root_dir, 'bin')
            if self.has_python:
            # if the application doesn't include python, we don't need these two lines
                pylib_path = os.path.join(env_root_dir, self.python_lib)
        else:
            lib_path = os.path.join(env_root_dir, 'lib', 'salome')
            bin_path = os.path.join(env_root_dir, 'bin', 'salome')
            if self.has_python:
            # if the application doesn't include python, we don't need these two lines
                pylib_path = os.path.join(env_root_dir, self.python_lib, 'salome')

        # Construct the paths to prepend to PATH and LD_LIBRARY_PATH and 
        # PYTHONPATH
        l_binpath_libpath.append( (bin_path, lib_path) )

        for bin_path, lib_path in l_binpath_libpath:
            if not self.forBuild:
                self.prepend('PATH', bin_path)
                if src.architecture.is_windows():
                    self.prepend('PATH', lib_path)
                else :
                    self.prepend('LD_LIBRARY_PATH', lib_path)

            l = [ bin_path, lib_path ]
            if not src.product.product_is_wheel(pi):
                if self.has_python:
                    l.append(pylib_path)
                self.prepend('PYTHONPATH', l)

    def set_cpp_env(self, product_info):
        """\
        Sets the generic environment for a SALOME cpp product.
        
        :param product_info Config: The product description
        """
        # Construct XXX_ROOT_DIR
        env_root_dir = self.get(product_info.name + "_ROOT_DIR")
        l_binpath_libpath = []

        # Construct the paths to prepend to PATH and LD_LIBRARY_PATH and 
        # PYTHONPATH
        bin_path = os.path.join(env_root_dir, 'bin')
        lib_path = os.path.join(env_root_dir, 'lib')
        l_binpath_libpath.append( (bin_path, lib_path) )

        for bin_path, lib_path in l_binpath_libpath:
            if not self.forBuild:
                self.prepend('PATH', bin_path)
                if src.architecture.is_windows():
                    self.prepend('PATH', lib_path)
                else :
                    self.prepend('LD_LIBRARY_PATH', lib_path)

            l = [ bin_path, lib_path ]
            if self.has_python:
                l.append(os.path.join(env_root_dir, self.python_lib))
            self.prepend('PYTHONPATH', l)

    def load_cfg_environment(self, cfg_env):
        """\
        Loads environment defined in cfg_env 
        
        :param cfg_env Config: A config containing an environment    
        """
        # Loop on cfg_env values
        for env_def in cfg_env:
            val = cfg_env[env_def]
            
            # if it is env_script, do not do anything (reserved keyword)
            if env_def == "env_script":
                continue
            
            # if it is a dict, do not do anything
            if isinstance(val, src.pyconf.Mapping):
                continue

            # if it is a list, loop on its values
            if isinstance(val, src.pyconf.Sequence):
                # transform into list of strings
                l_val = []
                for item in val:
                    l_val.append(item)
                val = l_val

            # "_" means that the value must be prepended
            if env_def.startswith("_"):
                # separator exception for PV_PLUGIN_PATH
                if env_def[1:] == 'PV_PLUGIN_PATH':
                    self.prepend(env_def[1:], val, ';')
                else:
                    self.prepend(env_def[1:], val)
            elif env_def.endswith("_"):
                # separator exception for PV_PLUGIN_PATH
                if env_def[:-1] == 'PV_PLUGIN_PATH':
                    self.append(env_def[:-1], val, ';')
                else:
                    self.append(env_def[:-1], val)
            else:
                self.set(env_def, val)

    def set_a_product(self, product, logger):
        """\
        Sets the environment of a product. 
        
        :param product str: The product name
        :param logger Logger: The logger instance to display messages
        """

        # Get the informations corresponding to the product
        pi = src.product.get_product_config(self.cfg, product)
        # skip compile time products at run time 
        if not self.forBuild:
            if src.product.product_is_compile_time(pi):
                return
        else:
            if src.product.product_is_native(pi) :
                self.set("SAT_%s_IS_NATIVE"%pi.name, "1")
                

        # skip pip products when pip is activated and installation is done in python 
        #if (src.appli_test_property(self.cfg,"pip", "yes") and 
        #    src.product.product_test_property(pi,"pip", "yes") and
        #    src.appli_test_property(self.cfg,"pip_install_dir", "python") ):
        #        return

        # skip mesa products (if any) at run time, 
        # unless use_mesa property was activated
        if not self.forBuild:
            if not ("APPLICATION" in self.cfg  and
                    "properties" in self.cfg.APPLICATION  and
                    "use_mesa" in self.cfg.APPLICATION.properties  and
                    self.cfg.APPLICATION.properties.use_mesa == "yes") :
                if ("properties" in pi and
                    "is_mesa" in pi.properties  and
                    pi.properties.is_mesa == "yes") :
                    logger.write(_("Skip mesa product %s\n") % pi.name, 4)
                    return
               
        
        if self.for_package:
            prod_base_name=os.path.basename(pi.install_dir)
            if prod_base_name.startswith("config"):
                # case of a products installed in base. We remove "config-i"
                prod_base_name=os.path.basename(os.path.dirname(pi.install_dir))
            pi.install_dir = os.path.join(
                                 "out_dir_Path",
                                 self.for_package,
                                 prod_base_name)

        if not self.silent:
            logger.write(_("Setting environment for %s\n") % product, 4)

        self.add_line(1)
        self.add_comment('setting environ for ' + product)
            
        # Do not define environment if the product is native
        if src.product.product_is_native(pi):
            if src.product.product_has_env_script(pi):
                self.run_env_script(pi, native=True)
            return
               
        # Set an additional environment for SALOME products
        if src.product.product_is_salome(pi):
            # set environment using definition of the product
            self.set_salome_minimal_product_env(pi, logger)
            self.set_salome_generic_product_env(pi)
           
        
        # Expand SALOME_MODULES variable for products which have a salome gui
        if src.product.product_has_salome_gui(pi):
            self.expand_salome_modules(pi)

        # use variable LICENCE_FILE to communicate the licence file name to the environment script
        licence_file_name = src.product.product_has_licence(pi, self.cfg.PATHS.LICENCEPATH)
        if licence_file_name:
            logger.write("licence file found for product %s : %s\n" % (pi.name, licence_file_name), 5) 
            self.set("LICENCE_FILE", licence_file_name)

        if src.product.product_is_cpp(pi):
            # set a specific environment for cpp modules
            self.set_salome_minimal_product_env(pi, logger)
            self.set_cpp_env(pi)
            
            if src.product.product_is_generated(pi):
                if "component_name" in pi:
                    # hack the source and install directories in order to point  
                    # on the generated product source install directories
                    install_dir_save = pi.install_dir
                    source_dir_save = pi.source_dir
                    name_save = pi.name
                    pi.install_dir = os.path.join(self.cfg.APPLICATION.workdir,
                                                  self.cfg.INTERNAL.config.install_dir,
                                                  pi.component_name)
                    if self.for_package:
                        pi.install_dir = os.path.join("out_dir_Path",
                                                      self.for_package,
                                                      pi.component_name)
                    pi.source_dir = os.path.join(self.cfg.APPLICATION.workdir,
                                                  "GENERATED",
                                                  pi.component_name)
                    pi.name = pi.component_name
                    self.set_salome_minimal_product_env(pi, logger)
                    self.set_salome_generic_product_env(pi)
                    
                    # Put original values
                    pi.install_dir = install_dir_save
                    pi.source_dir = source_dir_save
                    pi.name = name_save
        
        # Put the environment define in the configuration of the product
        if "environ" in pi:
            self.load_cfg_environment(pi.environ)
            if self.forBuild and "build" in pi.environ:
                self.load_cfg_environment(pi.environ.build)
            if not self.forBuild and "launch" in pi.environ:
                self.load_cfg_environment(pi.environ.launch)
            # if product_info defines a env_scripts, load it
            if 'env_script' in pi.environ:
                self.run_env_script(pi, logger)

        
            

    def run_env_script(self, product_info, logger=None, native=False):
        """\
        Runs an environment script. 
        
        :param product_info Config: The product description
        :param logger Logger: The logger instance to display messages
        :param native Boolean: if True load set_native_env instead of set_env
        """
        env_script = product_info.environ.env_script
        # Check that the script exists
        if not os.path.exists(env_script):
            raise src.SatException(_("Environment script not found: %s") % 
                                   env_script)

        if not self.silent and logger is not None:
            logger.write("  ** load %s\n" % env_script, 4)

        # import the script and run the set_env function
        try:
            import imp
            pyproduct = imp.load_source(product_info.name + "_env_script",
                                        env_script)
            if not native:
                if self.forBuild and "set_env_build" in dir(pyproduct):
                    pyproduct.set_env_build(self,
                                            product_info.install_dir,
                                            product_info.version)
                elif (not self.forBuild) and "set_env_launch" in dir(pyproduct):
                    pyproduct.set_env_launch(self,
                                            product_info.install_dir,
                                            product_info.version)
                else:
                    # at least this one is mandatory,
                    # if set_env_build and set_env_build are not defined
                    pyproduct.set_env(self,
                                      product_info.install_dir,
                                      product_info.version)
            else:
                # not mandatory, if set_nativ_env not defined, we do nothing
                if "set_nativ_env" in dir(pyproduct):
                    pyproduct.set_nativ_env(self)
        except:
            __, exceptionValue, exceptionTraceback = sys.exc_info()
            print(exceptionValue)
            import traceback
            traceback.print_tb(exceptionTraceback)
            traceback.print_exc()

    def set_products(self, logger, src_root=None):
        """\
        Sets the environment for all the products. 
        
        :param logger Logger: The logger instance to display messages
        :param src_root src: the application working directory
        """
        self.add_line(1)
        self.add_comment('setting environ for all products')

        # Make sure that the python lib dirs are set after python
        if "Python" in self.sorted_product_list:
            self.set_a_product("Python", logger)
            self.set_python_libdirs()

        # The loop on the products
        for product in self.sorted_product_list:
            if product == "Python":
                continue
            self.set_a_product(product, logger)
 
    def set_full_environ(self, logger, env_info):
        """\
        Sets the full environment for products, with their dependencies 
        specified in env_info dictionary. 
        
        :param logger Logger: The logger instance to display messages
        :param env_info list: the list of products
        """
        DBG.write("set_full_environ for", env_info)
        # DBG.write("set_full_environ config", self.cfg.APPLICATION.environ, True)
        # set product environ
        self.set_application_env(logger)

        # use the sorted list of all products to sort the list of products 
        # we have to set
        visited=[]
        from compile import depth_search_graph # to get the dependencies
        for p_name in env_info:
            visited=depth_search_graph(self.all_products_graph, p_name, visited)
        sorted_product_list=[]
        for n in self.sorted_product_list:
            if n in visited:
                sorted_product_list.append(n)

        if "Python" in sorted_product_list:
            self.set_a_product("Python", logger)
            self.set_python_libdirs()

        # set products
        for product in sorted_product_list:
            if product == "Python":
                continue
            self.set_a_product(product, logger)

class FileEnvWriter:
    """\
    Class to dump the environment to a file.
    """
    def __init__(self, config, logger, out_dir, src_root, env_info=None):
        """\
        Initialization.

        :param cfg Config: the global config
        :param logger Logger: The logger instance to display messages
        :param out_dir str: The directory path where t put the output files
        :param src_root str: The application working directory
        :param env_info str: The list of products to add in the files.
        """
        self.config = config
        self.logger = logger
        self.out_dir = out_dir
        self.src_root= src_root
        self.silent = True
        self.env_info = env_info

    def write_tcl_files(self,
                        forBuild, 
                        shell, 
                        for_package = None,
                        no_path_init=False,
                        additional_env = {}):
        """\
        Create tcl environment files for environment module.
        
        :param forBuild bool: if true, the build environment
        :param shell str: the type of file wanted (.sh, .bat)
        :param for_package bool: if true do specific stuff for required for packages
        :param no_path_init bool: if true generate a environ file that do not reinitialise paths
        :param additional_env dict: contains sat_ prefixed variables to help the génération, 
                                    and also variables to add in the environment.
        :return: The path to the generated file
        :rtype: str
        """

        # get the products informations
        all_products=self.config.APPLICATION.products
        products_infos = src.product.get_products_infos(all_products, self.config) 

        # set a global environment (we need it to resolve variable references
        # between dependent products
        global_environ = src.environment.SalomeEnviron(self.config,
                                  src.environment.Environ(additional_env),
                                  False)
        global_environ.set_products(self.logger)
        
        # The loop on the products
        for product in all_products:
            # create one file per product
            pi = src.product.get_product_config(self.config, product)
            if "base" not in pi:  # we write tcl files only for products in base
                continue

            # get the global environment, and complete it with sat_ prefixed 
            # prefixed variables which are used to transfer info to 
            # TclFileEnviron class  
            product_env = copy.deepcopy(global_environ.environ)
            product_env.environ["sat_product_name"] = pi.name
            product_env.environ["sat_product_version"] = pi.version
            product_env.environ["sat_product_base_path"] = src.get_base_path(self.config)
            product_env.environ["sat_product_base_name"] = pi.base
   
            # store infos in sat_product_load_depend to set dependencies in tcl file
            sat_product_load_depend=""
            for p_name,p_info in products_infos:
                if p_name in pi.depend:
                    sat_product_load_depend+="module load %s/%s/%s;" % (pi.base, 
                                                                        p_info.name, 
                                                                        p_info.version)
            if len(sat_product_load_depend)>0:
                # if there are dependencies, store the module to load (get rid of trailing ;)
                product_env.environ["sat_product_load_depend"]=sat_product_load_depend[0:-1]


            env_file_name = os.path.join(product_env.environ["sat_product_base_path"], 
                                         "modulefiles", 
                                         product_env.environ["sat_product_base_name"],
                                         product_env.environ["sat_product_name"], 
                                         product_env.environ["sat_product_version"])
            prod_dir_name=os.path.dirname(env_file_name)
            if not os.path.isdir(prod_dir_name):
                os.makedirs(prod_dir_name)

            env_file = open(env_file_name, "w")
            file_environ = src.fileEnviron.get_file_environ(env_file,
                                           "tcl", product_env)
            env = SalomeEnviron(self.config, 
                                file_environ, 
                                False, 
                                for_package=for_package)
            if "Python" in pi.depend:
                # short cut, env.python_lib is required by set_a_product for salome modules
                env.has_python="True"
                env.python_lib=global_environ.get("PYTHON_LIBDIR")
            env.set_a_product(product, self.logger)
            env_file.close()
            if not self.silent:
                self.logger.write(_("    Create tcl module environment file %s\n") % 
                                  src.printcolors.printcLabel(env_file_name), 3)


    def write_env_file(self,
                       filename,
                       forBuild, 
                       shell, 
                       for_package = None,
                       no_path_init=False,
                       additional_env = {}):
        """\
        Create an environment file.
        
        :param filename str: the file path
        :param forBuild bool: if true, the build environment
        :param shell str: the type of file wanted (.sh, .bat)
        :param for_package bool: if true do specific stuff for required for packages
        :param no_path_init bool: if true generate a environ file that do not reinitialise paths
        :param additional_env dict: contains sat_ prefixed variables to help the génération, 
                                    and also variables to add in the environment.
        :return: The path to the generated file
        :rtype: str
        """
        additional_env["sat_dist"]=self.config.VARS.dist
        if not self.silent:
            self.logger.write(_("Create environment file %s\n") % 
                              src.printcolors.printcLabel(filename), 3)
        # create then env object
        env_file = open(os.path.join(self.out_dir, filename), "w")

        # we duplicate additional_env, and transmit it to fileEnviron, which will use its sat_ prefixed variables.
        # the other variables of additional_env are added to the environement file at the end of this function.
        salome_env = copy.deepcopy(additional_env)
        file_environ = src.fileEnviron.get_file_environ(env_file,
                                               shell,
                                               src.environment.Environ(salome_env))
        if no_path_init:
            # specify we don't want to reinitialise paths
            # path will keep the inherited value, which will be appended with new values.
            file_environ.set_no_init_path()

        env = SalomeEnviron(self.config, 
                            file_environ, 
                            forBuild, 
                            for_package=for_package)

        env.silent = self.silent

        # Set the environment
        if self.env_info is not None:
            env.set_full_environ(self.logger, self.env_info)
        else:
            # set env from the APPLICATION
            env.set_application_env(self.logger)
            # set the products
            env.set_products(self.logger,
                            src_root=self.src_root)
        # Add the additional environment if it is not empty
        if len(additional_env) != 0:
            env.add_line(1)
            env.add_comment("[APPLI variables]")
            for variable in additional_env:
                if not variable.startswith("sat_"):
                    # by convention variables starting with sat_ are used to transfer information, 
                    # not to be written in env
                    env.set(variable, additional_env[variable])

        # finalise the writing and close the file
        env.finish()
        env_file.close()

        return env_file.name
   

class Shell:
    """\
    Definition of a Shell.
    """
    def __init__(self, name, extension):
        """\
        Initialization.

        :param name str: the shell name
        :param extension str: the shell extension
        """
        self.name = name
        self.extension = extension

def load_environment(config, build, logger):
    """\
    Loads the environment (used to run the tests, for example).
    
    :param config Config: the global config
    :param build bool: build environement if True
    :param logger Logger: The logger instance to display messages
    """
    environ = SalomeEnviron(config, Environ(os.environ), build)
    environ.set_application_env(logger)
    environ.set_products(logger)
