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

import src

# create bash product file
_bash_content = """PRODUCT_DIR=%s
if [[ "${ENV_FOR_LAUNCH}x" == "x" ]]
then
    export ENV_FOR_LAUNCH=1
fi

if [[ "${ENV_FOR_LAUNCH}" == "1" ]]
then
    source $PRODUCT_DIR/env_launch.sh
else
    source $PRODUCT_DIR/env_build.sh
fi
"""

# create batch product file
_batch_content = """set PRODUCT_DIR=%s
IF NOT DEFINED ENV_FOR_LAUNCH set ENV_FOR_LAUNCH=1

if "%%ENV_FOR_LAUNCH%%"=="1" (
    %%PRODUCT_DIR%%\\env_launch.bat
) else (
    %%PRODUCT_DIR%%\\env_build.bat
)
"""

class Environ:
    '''Class to manage the environment context
    '''
    def __init__(self, environ=None):
        '''Initialization. If the environ argument is passed, the environment
           will be add to it, else it is the external environment.
           
        :param environ dict:  
        '''
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ

    def __repr__(self):
        """easy non exhaustive quick resume for debug print
        """
        res={}
        res["environ"]=self.environ
        return self.__class__.__name__ + str(res)[0:-1] + " ...etc...}"

    def _expandvars(self, value):
        '''replace some $VARIABLE into its actual value in the environment
        
        :param value str: the string to be replaced
        :return: the replaced variable
        :rtype: str
        '''
        if "$" in value:
            # The string.Template class is a string class 
            # for supporting $-substitutions
            zt = string.Template(value)
            try:
                value = zt.substitute(self.environ)
            except KeyError as exc:
                raise src.SatException(_("Missing definition "
                                         "in environment: %s") % str(exc))
        return value

    def append_value(self, key, value, sep=os.pathsep):
        '''append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        '''
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
        '''Same as append_value but the value argument can be a list
        
        :param key str: the environment variable to append
        :param value str or list: the value(s) to append to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            for v in value:
                self.append_value(key, v, sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=os.pathsep):
        '''prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        '''
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
        '''Same as prepend_value but the value argument can be a list
        
        :param key str: the environment variable to prepend
        :param value str or list: the value(s) to prepend to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            for v in value:
                self.prepend_value(key, v, sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        '''Check if the key exists in the environment
        
        :param key str: the environment variable to check
        '''
        return self.environ.has_key(key)

    def set(self, key, value):
        '''Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        '''
        self.environ[key] = self._expandvars(value)

    def get(self, key):
        '''Get the value of the environment variable "key"
        
        :param key str: the environment variable
        '''
        if key in self.environ:
            return self.environ[key]
        else:
            return ""

    def command_value(self, key, command):
        '''Get the value given by the system command "command" 
           and put it in the environment variable key
        
        :param key str: the environment variable
        :param command str: the command to execute
        '''
        value = subprocess.Popen(command,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 env=self.environ).communicate()[0]
        self.environ[key] = value


class SalomeEnviron:
    """Class to manage the environment of SALOME.
    """

    def __init__(self, cfg, environ, forBuild=False):
        self.environ = environ
        self.cfg = cfg
        self.forBuild = forBuild
        self.silent = False

    def __repr__(self):
        """easy non exhaustive quick resume for debug print"""
        res={}
        res["environ"]=str(self.environ)
        res["forBuild"]=self.forBuild
        return self.__class__.__name__ + str(res)[0:-1] + " ...etc...}"

    def append(self, key, value, sep=os.pathsep):
        return self.environ.append(key, value, sep)

    def prepend(self, key, value, sep=os.pathsep):
        return self.environ.prepend(key, value, sep)

    def is_defined(self, key):
        return self.environ.is_defined(key)

    def get(self, key):
        return self.environ.get(key)

    def set(self, key, value):
        # check if value needs to be evaluated
        if value is not None and value.startswith("`") and value.endswith("`"):
            res = subprocess.Popen("echo %s" % value, shell=True, stdout=subprocess.PIPE).communicate()
            value = res[0].strip()

        return self.environ.set(key, value)

    def dump(self, out):
        """Write the environment to out"""
        for k in self.environ.environ.keys():
            try:
                value = self.get(k)
            except:
                value = "?"
            out.write("%s=%s\n" % (k, value))

    def add_line(self, nb_line):
        if 'add_line' in dir(self.environ):
            self.environ.add_line(nb_line)

    def add_comment(self, comment):
        if 'add_comment' in dir(self.environ):
            self.environ.add_comment(comment)

    def add_warning(self, warning):
        if 'add_warning' in dir(self.environ):
            self.environ.add_warning(warning)

    def finish(self, required):
        if 'finish' in dir(self.environ):
            self.environ.add_line(1)
            self.environ.add_comment("clean all the path")
            self.environ.finish(required)

    def list_version_4_prereq(self, prerequisite, logger):
        alist = []
        for path in self.cfg.TOOLS.environ.prereq_install_dir:
            if not os.path.exists(path):
                continue
            prereqlist = os.listdir(path)
            for prereq in prereqlist:
                if prereq.split("-")[0] == prerequisite:
                    #logger.error(str(prereq) + "\n")
                    alist.append(str(prereq))

        if len(alist) > 0:
            logger.write(_("Available prerequisites are:") + "\n\t%s\n" % '\n\t'.join(alist), 2)

    def set_python_libdirs(self):
        if src.architecture.is_windows():
            # sysconfig.get_python_lib() does not return appropriate path on Windows
            # clearly decide here once for windows
            ver = self.get('PYTHON_VERSION')
            self.set('PYTHON_LIBDIR0', os.path.join('lib', 'python' + ver, 'site-packages'))
            self.set('PYTHON_LIBDIR1', os.path.join('lib64', 'python' + ver, 'site-packages'))

        else:
            ver = self.get('PYTHON_VERSION')
            self.set('PYTHON_LIBDIR0', os.path.join('lib', 'python' + ver, 'site-packages'))
            self.set('PYTHON_LIBDIR1', os.path.join('lib64', 'python' + ver, 'site-packages'))
          
        self.python_lib0 = self.get('PYTHON_LIBDIR0')
        self.python_lib1 = self.get('PYTHON_LIBDIR1')

    ##
    # Get the products name to add in SALOME_MODULES environment variable
    # It is the name of the product, except in the case where the is a component name.
    # And it has to be in SALOME_MODULES variable only if has_gui = "yes"
    def getNames(self, lProducts):
        lProdHasGui = [p for p in lProducts if 'has_gui' in src.product.get_product_config(self.cfg, p) and src.product.get_product_config(self.cfg, p).has_gui=='yes']
        lProdName = []
        for ProdName in lProdHasGui:
            pi = src.product.get_product_config(self.cfg, ProdName)
            if 'component_name' in pi:
                lProdName.append(pi.component_name)
            else:
                lProdName.append(ProdName)
        return lProdName

    ##
    # Sets the environment defined in the PRODUCT file.
    def set_application_env(self, logger):
        if 'environ' in self.cfg.APPLICATION:
            self.add_comment("APPLICATION environment")
            for p in self.cfg.APPLICATION.environ:
                self.set(p, self.cfg.APPLICATION.environ[p])
            self.add_line(1)

        if 'environ_script' in self.cfg.APPLICATION:
            for pscript in self.cfg.APPLICATION.environ_script:
                self.add_comment("script %s" % pscript)
                sname = pscript.replace(" ", "_")
                self.run_env_script("APPLICATION_%s" % sname, self.cfg.APPLICATION.environ_script[pscript], logger)
                self.add_line(1)
        
        if 'profile' in self.cfg.APPLICATION:
            profile_product = self.cfg.APPLICATION.profile.product
            product_info_profile = src.product.get_product_config(self.cfg, profile_product)
            profile_share_salome = os.path.join( product_info_profile.install_dir, "share", "salome" )
            self.set( "SUITRoot", profile_share_salome )
            self.set( "SalomeAppConfig", os.path.join( profile_share_salome, "resources", profile_product.lower() ) )
        
        # The list of products to launch
        lProductsName = self.getNames(self.cfg.APPLICATION.products.keys())
        
        self.set( "SALOME_MODULES",    ','.join(lProductsName))

    ##
    # Set xxx_ROOT_DIR and xxx_SRC_DIR.
    def set_salome_minimal_product_env(self, product_info, logger, single_dir, cfgdic=None):
        # set root dir
        root_dir = product_info.name + "_ROOT_DIR"
        indic = cfgdic is not None and root_dir in cfgdic
        if not self.is_defined(root_dir) and not indic:
            if single_dir:
                self.set(root_dir, os.path.join(self.get('INSTALL_ROOT'), 'SALOME'))
            elif 'install_dir' in product_info and product_info.install_dir:
                self.set(root_dir, product_info.install_dir)
            elif not self.silent:
                logger.write("  " + _("No install_dir for product %s\n") % product_info.name, 5)

        # set source dir, unless the product is fixed (no source dir)
        if not src.product.product_is_fixed(product_info):
            src_dir = product_info.name + "_SRC_DIR"
            indic = cfgdic is not None and src_dir in cfgdic
            if not self.is_defined(src_dir) and not indic:
                self.set(src_dir, product_info.source_dir)

    def set_salome_generic_product_env(self, product):
        pi = src.product.get_product_config(self.cfg, product)
        env_root_dir = self.get(pi.name + "_ROOT_DIR")
        l_binpath_libpath = []

        # create additional ROOT_DIR for CPP components
        if 'component_name' in pi:
            compo_name = pi.component_name
            if compo_name + "CPP" == product:
                compo_root_dir = compo_name + "_ROOT_DIR"
                envcompo_root_dir = os.path.join( self.cfg.TOOLS.common.install_root, compo_name )
                self.set(compo_root_dir ,  envcompo_root_dir)
                bin_path = os.path.join(envcompo_root_dir, 'bin', 'salome')
                lib_path = os.path.join(envcompo_root_dir, 'lib', 'salome')
                l_binpath_libpath.append( (bin_path, lib_path) )

        appliname = 'salome'
        if src.get_cfg_param(pi, 'product_type', 'SALOME').upper() not in [ "SALOME", "SMESH_PLUGIN", "SAMPLE" ]:
            appliname = ''

        bin_path = os.path.join(env_root_dir, 'bin', appliname)
        lib_path = os.path.join(env_root_dir, 'lib', appliname)
        l_binpath_libpath.append( (bin_path, lib_path) )

        for bin_path, lib_path in l_binpath_libpath:
            if not self.forBuild:
                self.prepend('PATH', bin_path)
                if src.architecture.is_windows():
                    self.prepend('PATH', lib_path)
                else :
                    self.prepend('LD_LIBRARY_PATH', lib_path)

            l = [ bin_path, lib_path,
                  os.path.join(env_root_dir, self.python_lib0, appliname),
                  os.path.join(env_root_dir, self.python_lib1, appliname)
                ]
            self.prepend('PYTHONPATH', l)

    ##
    # Loads environment define in the configuration.
    def load_cfg_environment(self, cfg_env):
        for env_def in cfg_env:
            val = cfg_env[env_def]
            if isinstance(val, src.pyconf.Mapping):
                continue

            if isinstance(val, src.pyconf.Sequence):
                # transform into list of strings
                l_val = []
                for item in val:
                    l_val.append(item)
                val = l_val

            if env_def.startswith("_"):
                # separator exception for PV_PLUGIN_PATH
                if env_def[1:] == 'PV_PLUGIN_PATH':
                    self.prepend(env_def[1:], val, ';')
                else:
                    self.prepend(env_def[1:], val)
            elif env_def.endswith("_"):
                # separator exception for PV_PLUGIN_PATH
                if env_def[:-1] == 'PV_PLUGIN_PATH':
                    self.prepend(env_def[:-1], val, ';')
                else:
                    self.prepend(env_def[:-1], val)
            else:
                self.set(env_def, val)

    ##
    # Sets the environment of a product.
    def set_a_product(self, product, logger, single_dir):
               
        if not self.silent:
            logger.write(_("Setting environment for %s\n") % product, 4)

        self.add_line(1)
        self.add_comment('setting environ for ' + product)
        
        pi = src.product.get_product_config(self.cfg, product)

        # Do not define environment if the product is native or fixed
        if src.product.product_is_native(pi):
            return

        if "environ" in pi:
            # set environment using definition of the product
            self.set_salome_minimal_product_env(pi, logger, single_dir, pi.environ)
            self.set_salome_generic_product_env(product)
            self.load_cfg_environment(pi.environ)
            if self.forBuild and "build" in pi.environ:
                self.load_cfg_environment(pi.environ.build)
            if not self.forBuild and "launch" in pi.environ:
                self.load_cfg_environment(pi.environ.launch)
        else:
            # no environment defined in config
            self.set_salome_minimal_product_env(pi, logger, single_dir)
            if 'install_dir' in pi :
                self.set_salome_generic_product_env(product)

        # if product_info defines a env_scripts load it
        if 'env_script' in pi:
            self.run_env_script(pi, logger)
            

    ##
    # Runs an environment script.
    def run_env_script(self, product_info, logger=None):
        env_script = product_info.env_script
        if not os.path.exists(product_info.env_script):
            raise src.SatException(_("Environment script not found: %s") % env_script)

        if not self.silent and logger is not None:
            logger.write("  ** load %s\n" % product_info.env_script, 4)

        try:
            import imp
            pyproduct = imp.load_source(product_info.name + "_env_script", env_script)
            pyproduct.set_env(self, product_info.install_dir, product_info.version)
        except:
            __, exceptionValue, exceptionTraceback = sys.exc_info()
            print(exceptionValue)
            import traceback
            traceback.print_tb(exceptionTraceback)
            traceback.print_exc()

    ##
    # Sets the environment for all the products.
    def set_products(self, logger, src_root=None, single_dir=False):
        self.add_line(1)
        self.add_comment('setting environ for all products')

        self.set_python_libdirs()

        if src_root is None:
            src_root = self.cfg.APPLICATION.workdir
        self.set('SRC_ROOT', src_root)

        appli_name = "APPLI"
        if "APPLI" in self.cfg and "application_name" in self.cfg.APPLI:
            appli_name = self.cfg.APPLI.application_name
        self.set("SALOME_APPLI_ROOT", os.path.join(self.cfg.APPLICATION.workdir, appli_name))

        if not single_dir:
            single_dir = src.get_cfg_param(self.cfg.APPLICATION, "compil_in_single_dir", "no") == 'yes'

        for product in src.get_cfg_param(self.cfg.APPLICATION, "imported_products", []):
            self.set_a_product(product, logger, single_dir=single_dir)
            self.finish(False)

        for product in self.cfg.APPLICATION.products.keys():
            self.set_a_product(product, logger, single_dir=single_dir)
            self.finish(False)

   
    ##
    # Sets the full environment for prerequisites and products specified in env_info dictionary.
    def set_full_environ(self, logger, env_info):
        # set product environ
        self.set_application_env(logger)

        # set products
        install_root = os.path.join(self.cfg.APPLICATION.workdir, "INSTALL")
        source_root = os.path.join(self.cfg.APPLICATION.workdir, "SOURCES")
        self.set('INSTALL_ROOT', install_root)
        self.set('SRC_ROOT', source_root)
        self.set_python_libdirs()

        single_dir = src.get_cfg_param(self.cfg.APPLICATION, "compil_in_single_dir", "no") == 'yes'
        for product in env_info['products']:
            self.set_a_product(product, logger, single_dir=single_dir)

##
# Class to dump the environment to a file.
class FileEnvWriter:
    def __init__(self, config, logger, out_dir, src_root, single_dir, env_info=None):
        self.config = config
        self.logger = logger
        self.out_dir = out_dir
        self.src_root= src_root
        self.single_dir = single_dir
        self.silent = True
        self.env_info = env_info

    def write_env_file(self, filename, forBuild, shell):
        """Create an environment file."""
        if not self.silent:
            self.logger.write(_("Create environment file %s\n") % src.printcolors.printcLabel(filename), 3)

        # create then env object
        env_file = open(os.path.join(self.out_dir, filename), "w")
        tmp = src.fileEnviron.get_file_environ(env_file, shell, {}, self.config )
        env = SalomeEnviron(self.config, tmp, forBuild)
        env.silent = self.silent

        if self.env_info is not None:
            env.set_full_environ(self.logger, self.env_info)
        else:
            # set env from PRODUCT
            env.set_application_env(self.logger)
            # set the products
            env.set_products(self.logger,
                            src_root=self.src_root, single_dir=self.single_dir)

        # add cleanup and close
        env.finish(True)
        env_file.close()

        return env_file.name

    def write_product_file(self, filename, shell):
        """Create a product file."""
        if not self.silent:
            self.logger.write(_("Create product file %s\n") % src.printcolors.printcLabel(filename), 3)

        prod_file = open(os.path.join(self.out_dir, filename), "w")
        if shell == "bash":
            content = _bash_content % self.out_dir
        elif shell == "batch":
            content = _batch_content % self.out_dir
        else:
            raise src.SatException(_("Unknown shell: %s") % shell)

        prod_file.write(content)
        prod_file.close()
       
        return prod_file.name
   
    def write_cfgForPy_file(self, aFile, additional_env = {}):
        """append to current opened aFile a cfgForPy environment (python syntax)."""
        if not self.silent:
            self.logger.write(_("Create configuration file %s\n") % src.printcolors.printcLabel(aFile.name), 3)

        # create then env object
        tmp = src.fileEnviron.get_file_environ(aFile, "cfgForPy", {}, self.config)
        forBuild = True
        forLaunch = False
        env = SalomeEnviron(self.config, tmp, forLaunch)
        env.silent = self.silent

        if self.env_info is not None:
            env.set_full_environ(self.logger, self.env_info)
        else:
            # set env from PRODUCT
            env.set_application_env(self.logger)
            # set the prerequisites
            env.set_prerequisites(self.logger)
            # set the products
            env.set_products(self.logger,
                            src_root=self.src_root, single_dir=self.single_dir)

        if len(additional_env) != 0:
            for variable in additional_env:
                env.set(variable, additional_env[variable])

        # add cleanup and close
        env.finish(True)

##
# Definition of a Shell.
class Shell:
    def __init__(self, name, extension):
        self.name = name
        self.extension = extension

##
# Loads the environment (used to run the tests).
def load_environment(config, build, logger):
    environ = SalomeEnviron(config, Environ(os.environ), build)
    environ.set_application_env(logger)
    environ.set_products(logger)
    environ.finish(True)