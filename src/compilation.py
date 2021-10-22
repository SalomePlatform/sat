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
import sys
import shutil
import glob

import src

C_COMPILE_ENV_LIST = ["CC",
                      "CXX",
                      "F77",
                      "CFLAGS",
                      "CXXFLAGS",
                      "LIBS",
                      "LDFLAGS"]

class Builder:
    """Class to handle all construction steps, like cmake, configure, make, ...
    """
    def __init__(self,
                 config,
                 logger,
                 product_name,
                 product_info,
                 options = src.options.OptResult(),
                 check_src=True):
        self.config = config
        self.logger = logger
        self.options = options
        self.product_name = product_name
        self.product_info = product_info
        self.build_dir = src.Path(self.product_info.build_dir)
        self.source_dir = src.Path(self.product_info.source_dir)
        self.install_dir = src.Path(self.product_info.install_dir)
        self.header = ""
        self.debug_mode = False
        if "debug" in self.product_info and self.product_info.debug == "yes":
            self.debug_mode = True
        self.verbose_mode = False
        if "verbose" in self.product_info and self.product_info.verbose == "yes":
            self.verbose_mode = True

    ##
    # Shortcut method to log in log file.
    def log(self, text, level, showInfo=True):
        self.logger.write(text, level, showInfo)
        self.logger.logTxtFile.write(src.printcolors.cleancolor(text))
        self.logger.flush()

    ##
    # Shortcut method to log a command.
    def log_command(self, command):
        self.log("> %s\n" % command, 5)

    ##
    # Prepares the environment.
    # Build two environment: one for building and one for testing (launch).
    def prepare(self, add_env_launch=False):

        if not self.build_dir.exists():
            # create build dir
            self.build_dir.make()

        self.log('  build_dir   = %s\n' % str(self.build_dir), 4)
        self.log('  install_dir = %s\n' % str(self.install_dir), 4)
        self.log('\n', 4)

        # add products in depend and opt_depend list recursively
        environ_info = src.product.get_product_dependencies(self.config,
                                                            self.product_name,
                                                            self.product_info)
        #environ_info.append(self.product_info.name)

        # create build environment
        self.build_environ = src.environment.SalomeEnviron(self.config,
                                      src.environment.Environ(dict(os.environ)),
                                      True)
        self.build_environ.silent = (self.config.USER.output_verbose_level < 5)
        self.build_environ.set_full_environ(self.logger, environ_info)
        
        if add_env_launch:
        # create runtime environment
            self.launch_environ = src.environment.SalomeEnviron(self.config,
                                      src.environment.Environ(dict(os.environ)),
                                      False)
            self.launch_environ.silent = True # no need to show here
            self.launch_environ.set_full_environ(self.logger, environ_info)

        for ee in C_COMPILE_ENV_LIST:
            vv = self.build_environ.get(ee)
            if len(vv) > 0:
                self.log("  %s = %s\n" % (ee, vv), 4, False)

        return 0

    ##
    # Runs cmake with the given options.
    def cmake(self, options=""):

        cmake_option = options
        # cmake_option +=' -DCMAKE_VERBOSE_MAKEFILE=ON -DSALOME_CMAKE_DEBUG=ON'
        if 'cmake_options' in self.product_info:
            cmake_option += " %s " % " ".join(
                                        self.product_info.cmake_options.split())

        # add debug option
        if self.debug_mode:
            cmake_option += " -DCMAKE_BUILD_TYPE=Debug"
        else :
            cmake_option += " -DCMAKE_BUILD_TYPE=Release"

        # add verbose option if specified in application for this product.
        if self.verbose_mode:
            cmake_option += " -DCMAKE_VERBOSE_MAKEFILE=ON"

        # In case CMAKE_GENERATOR is defined in environment, 
        # use it in spite of automatically detect it
        if 'cmake_generator' in self.config.APPLICATION:
            cmake_option += " -DCMAKE_GENERATOR=\"%s\"" \
                                       % self.config.APPLICATION.cmake_generator
        command = ("cmake %s -DCMAKE_INSTALL_PREFIX=%s %s" %
                            (cmake_option, self.install_dir, self.source_dir))

        self.log_command(command)
        # for key in sorted(self.build_environ.environ.environ.keys()):
            # print key, "  ", self.build_environ.environ.environ[key]
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.put_txt_log_in_appli_log_dir("cmake")
        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs build_configure with the given options.
    def build_configure(self, options=""):

        if 'buildconfigure_options' in self.product_info:
            options += " %s " % self.product_info.buildconfigure_options

        command = str('%s/build_configure') % (self.source_dir)
        command = command + " " + options
        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)
        self.put_txt_log_in_appli_log_dir("build_configure")
        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs configure with the given options.
    def configure(self, options=""):

        if 'configure_options' in self.product_info:
            options += " %s " % self.product_info.configure_options

        command = "%s/configure --prefix=%s" % (self.source_dir,
                                                str(self.install_dir))

        command = command + " " + options
        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)
        
        self.put_txt_log_in_appli_log_dir("configure")
        if res == 0:
            return res
        else:
            return 1

    def hack_libtool(self):
        if not os.path.exists(str(self.build_dir + 'libtool')):
            return

        lf = open(os.path.join(str(self.build_dir), "libtool"), 'r')
        for line in lf.readlines():
            if 'hack_libtool' in line:
                return

        # fix libtool by replacing CC="<compil>" with hack_libtool function
        hack_command='''sed -i "s%^CC=\\"\(.*\)\\"%hack_libtool() { \\n\\
if test \\"\$(echo \$@ | grep -E '\\\\\\-L/usr/lib(/../lib)?(64)? ')\\" == \\\"\\\" \\n\\
  then\\n\\
    cmd=\\"\\1 \$@\\"\\n\\
  else\\n\\
    cmd=\\"\\1 \\"\`echo \$@ | sed -r -e 's|(.*)-L/usr/lib(/../lib)?(64)? (.*)|\\\\\\1\\\\\\4 -L/usr/lib\\\\\\3|g'\`\\n\\
  fi\\n\\
  \$cmd\\n\\
}\\n\\
CC=\\"hack_libtool\\"%g" libtool'''

        self.log_command(hack_command)
        subprocess.call(hack_command,
                        shell=True,
                        cwd=str(self.build_dir),
                        env=self.build_environ.environ.environ,
                        stdout=self.logger.logTxtFile,
                        stderr=subprocess.STDOUT)


    ##
    # Runs make to build the module.
    def make(self, nb_proc, make_opt=""):

        # make
        command = 'make'
        command = command + " -j" + str(nb_proc)
        command = command + " " + make_opt
        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)
        self.put_txt_log_in_appli_log_dir("make")
        if res == 0:
            return res
        else:
            return 1
    
    ##
    # Runs msbuild to build the module.
    def wmake(self,nb_proc, opt_nb_proc = None):

        hh = 'MSBUILD /m:%s' % str(nb_proc)
        if self.debug_mode:
            hh += " " + src.printcolors.printcWarning("DEBUG")
        # make
        command = 'msbuild'
        command = command + " /maxcpucount:" + str(nb_proc)
        if self.debug_mode:
            command = command + " /p:Configuration=Debug  /p:Platform=x64 "
        else:
            command = command + " /p:Configuration=Release /p:Platform=x64 "
        command = command + " ALL_BUILD.vcxproj"

        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)
        
        self.put_txt_log_in_appli_log_dir("make")
        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs 'make install'.
    def install(self):
        if src.architecture.is_windows():
            command = 'msbuild INSTALL.vcxproj'
            if self.debug_mode:
                command = command + " /p:Configuration=Debug  /p:Platform=x64 "
            else:
                command = command + " /p:Configuration=Release  /p:Platform=x64 "
        else :
            command = 'make install'
        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)
        
        res_check=self.check_install()
        if res_check > 0 :
            self.log_command("Error in sat check install - some files are not installed!")
        self.put_txt_log_in_appli_log_dir("makeinstall")

        res+=res_check
        if res == 0:
            return res
        else:
            return 1

    # this function checks wether a list of file patterns (specified by check_install keyword) 
    # exixts after the make install. The objective is to ensure the installation is complete.
    # patterns are given relatively to the install dir of the product
    def check_install(self):
        res=0
        if "check_install" in self.product_info:
            self.log_command("Check installation of files")
            for pattern in self.product_info.check_install:
                # pattern is given relatively to the install dir
                complete_pattern=os.path.join(self.product_info.install_dir, pattern) 
                self.log_command("    -> check %s" % complete_pattern)
                # expansion of pattern : takes into account environment variables and unix shell rules
                list_of_path=glob.glob(os.path.expandvars(complete_pattern))
                if not list_of_path:
                    # we expect to find at least one entry, if not we consider the test failed
                    res+=1
                    self.logger.write("Error, sat check install failed for file pattern %s\n" % complete_pattern, 1)
                    self.log_command("Error, sat check install failed for file pattern %s" % complete_pattern)
        return res

    ##
    # Runs 'make_check'.
    def check(self, command=""):
        if src.architecture.is_windows():
            cmd = 'msbuild RUN_TESTS.vcxproj /p:Configuration=Release  /p:Platform=x64 '
        else :
            if self.product_info.build_source=="autotools" :
                cmd = 'make check'
            else:
                cmd = 'make test'
        
        if command:
            cmd = command
        
        self.log_command(cmd)
        self.log_command("For more detailed logs, see test logs in %s" % self.build_dir)

        res = subprocess.call(cmd,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.launch_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.put_txt_log_in_appli_log_dir("makecheck")
        if res == 0:
            return res
        else:
            return 1
      
    ##
    # Performs a default build for this module.
    def do_default_build(self,
                         build_conf_options="",
                         configure_options="",
                         show_warning=True):
        use_autotools = False
        if 'use_autotools' in self.product_info:
            uc = self.product_info.use_autotools
            if uc in ['always', 'yes']: 
                use_autotools = True
            elif uc == 'option': 
                use_autotools = self.options.autotools


        self.use_autotools = use_autotools

        use_ctest = False
        if 'use_ctest' in self.product_info:
            uc = self.product_info.use_ctest
            if uc in ['always', 'yes']: 
                use_ctest = True
            elif uc == 'option': 
                use_ctest = self.options.ctest

        self.use_ctest = use_ctest

        if show_warning:
            cmd = ""
            if use_autotools: cmd = "(autotools)"
            if use_ctest: cmd = "(ctest)"
            
            self.log("\n", 4, False)
            self.log("%(module)s: Run default compilation method %(cmd)s\n" % \
                { "module": self.module, "cmd": cmd }, 4)

        if use_autotools:
            if not self.prepare(): return self.get_result()
            if not self.build_configure(
                                   build_conf_options): return self.get_result()
            if not self.configure(configure_options): return self.get_result()
            if not self.make(): return self.get_result()
            if not self.install(): return self.get_result()
            if not self.clean(): return self.get_result()
           
        else: # CMake
            if self.config.VARS.dist_name=='Win':
                if not self.wprepare(): return self.get_result()
                if not self.cmake(): return self.get_result()
                if not self.wmake(): return self.get_result()
                if not self.install(): return self.get_result()
                if not self.clean(): return self.get_result()
            else :
                if not self.prepare(): return self.get_result()
                if not self.cmake(): return self.get_result()
                if not self.make(): return self.get_result()
                if not self.install(): return self.get_result()
                if not self.clean(): return self.get_result()

        return self.get_result()

    ##
    # Performs a build with a script.
    def do_python_script_build(self, script, nb_proc):
        # script found
        self.logger.write(_("Compile %(product)s using script %(script)s\n") % \
            { 'product': self.product_info.name,
             'script': src.printcolors.printcLabel(script) }, 4)
        try:
            import imp
            product = self.product_info.name
            pymodule = imp.load_source(product + "_compile_script", script)
            self.nb_proc = nb_proc
            retcode = pymodule.compil(self.config, self, self.logger)
        except:
            __, exceptionValue, exceptionTraceback = sys.exc_info()
            self.logger.write(str(exceptionValue), 1)
            import traceback
            traceback.print_tb(exceptionTraceback)
            traceback.print_exc()
            retcode = 1
        finally:
            self.put_txt_log_in_appli_log_dir("script")

        return retcode

    def complete_environment(self, make_options):
        assert self.build_environ is not None
        # pass additional variables to environment 
        # (may be used by the build script)
        self.build_environ.set("APPLICATION_NAME", self.config.APPLICATION.name)
        self.build_environ.set("SOURCE_DIR", str(self.source_dir))
        self.build_environ.set("INSTALL_DIR", str(self.install_dir))
        self.build_environ.set("PRODUCT_INSTALL", str(self.install_dir))
        self.build_environ.set("BUILD_DIR", str(self.build_dir))
        self.build_environ.set("PRODUCT_BUILD", str(self.build_dir))
        self.build_environ.set("MAKE_OPTIONS", make_options)
        self.build_environ.set("DIST_NAME", self.config.VARS.dist_name)
        self.build_environ.set("DIST_VERSION", self.config.VARS.dist_version)
        self.build_environ.set("DIST", self.config.VARS.dist)
        self.build_environ.set("VERSION", self.product_info.version)
        # if product is in hpc mode, set SAT_HPC to 1 
        # in order for the compilation script to take it into account
        if src.product.product_is_hpc(self.product_info):
            self.build_environ.set("SAT_HPC", "1")
        if self.debug_mode:
            self.build_environ.set("SAT_DEBUG", "1")
        if self.verbose_mode:
            self.build_environ.set("SAT_VERBOSE", "1")


    def do_batch_script_build(self, script, nb_proc):

        if src.architecture.is_windows():
            make_options = "/maxcpucount:%s" % nb_proc
        else :
            make_options = "-j%s" % nb_proc

        self.log_command("  " + _("Run build script %s\n") % script)
        self.complete_environment(make_options)
        
        res = subprocess.call(script, 
                              shell=True,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ)

        res_check=self.check_install()
        if res_check > 0 :
            self.log_command("Error in sat check install - some files are not installed!")

        self.put_txt_log_in_appli_log_dir("script")
        res += res_check
        if res == 0:
            return res
        else:
            return 1
    
    def do_script_build(self, script, number_of_proc=0):
        # define make options (may not be used by the script)
        if number_of_proc==0:
            nb_proc = src.get_cfg_param(self.product_info,"nb_proc", 0)
            if nb_proc == 0: 
                nb_proc = self.config.VARS.nb_proc
        else:
            nb_proc = min(number_of_proc, self.config.VARS.nb_proc)
            
        extension = script.split('.')[-1]
        if extension in ["bat","sh"]:
            return self.do_batch_script_build(script, nb_proc)
        if extension == "py":
            return self.do_python_script_build(script, nb_proc)
        
        msg = _("The script %s must have .sh, .bat or .py extension." % script)
        raise src.SatException(msg)
    
    def put_txt_log_in_appli_log_dir(self, file_name):
        '''Put the txt log (that contain the system logs, like make command
           output) in the directory <APPLICATION DIR>/LOGS/<product_name>/
    
        :param file_name Str: the name of the file to write
        '''
        if self.logger.logTxtFile == sys.__stdout__:
            return
        dir_where_to_put = os.path.join(self.config.APPLICATION.workdir,
                                        "LOGS",
                                        self.product_info.name)
        file_path = os.path.join(dir_where_to_put, file_name)
        src.ensure_path_exists(dir_where_to_put)
        # write the logTxtFile copy it to the destination, and then recreate 
        # it as it was
        self.logger.logTxtFile.close()
        shutil.move(self.logger.txtFilePath, file_path)
        self.logger.logTxtFile = open(str(self.logger.txtFilePath), 'w')
        self.logger.logTxtFile.write(open(file_path, "r").read())
        
