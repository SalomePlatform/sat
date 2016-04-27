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

import src

C_COMPILE_ENV_LIST = ["CC",
                      "CXX",
                      "F77",
                      "CFLAGS",
                      "CXXFLAGS",
                      "LIBS",
                      "LDFLAGS"]

class CompilationResult:
    def __init__(self):
        self.prepare = False
        self.buildconfigure = False
        self.configure = False
        self.cmake = False
        self.make = False
        self.install = False
        self.check = False
        self.check_tried = False
        self.ignored = False
        self.reason = ""

    def isOK(self):
        if self.ignored:
            return False

        return self.prepare \
            and self.buildconfigure \
            and self.configure \
            and self.cmake \
            and self.make \
            and self.install \
            and self.check

    def setAllFail(self):
        self.prepare = False
        self.buildconfigure = False
        self.configure = False
        self.cmake = False
        self.make = False
        self.install = False
        self.check = False

    def setIgnored(self, reason=None):
        self.ignored = True
        if reason:
            self.reason = reason
        else:
            self.reason = _("ignored")

    def getErrorText(self):
        if self.ignored or len(self.reason):
            return self.reason

        if not self.prepare: return "PREPARE BUILD"
        if not self.buildconfigure: return "BUILD CONFIGURE"
        if not self.configure: return "CONFIGURE"
        if not self.cmake: return "CMAKE"
        if not self.make: return "MAKE"
        if not self.install: return "INSTALL"
        if not self.check: return "CHECK"
        
        return ""

class Builder:
    """Class to handle all construction steps, like cmake, configure, make, ...
    """
    def __init__(self, config, logger, options, product_info, debug_mode=False, check_src=True):
        self.config = config
        self.logger = logger
        self.options = options
        self.product_info = product_info
        self.build_dir = src.Path(self.product_info.build_dir)
        self.source_dir = src.Path(self.product_info.source_dir)
        self.install_dir = src.Path(self.product_info.install_dir)
        self.header = ""
        self.debug_mode = debug_mode

        if not self.source_dir.exists() and check_src:
            raise src.SatException(_("No sources found for product %(product)s in %(source_dir)s" % \
                { "product": self.product_info.name, "source_dir": self.source_dir } ))

        """
        # check that required modules exist
        for dep in self.product_info.depend:
            assert dep in self.config.TOOLS.src.product_info, "UNDEFINED product: %s" % dep
            dep_info = self.config.TOOLS.src.product_info[dep]
            if 'install_dir' in dep_info and not os.path.exists(dep_info.install_dir):
                raise src.SatException(_("Module %s is required") % dep)
        """
        self.results = CompilationResult()

    ##
    # Shortcut method to log in both log files.
    def log(self, text, level, showInfo=True):
        self.logger.write(text, level, showInfo)
        self.logger.logTxtFile.write(src.printcolors.cleancolor(text))

    ##
    # Shortcut method to log a command.
    def log_command(self, command):
        self.log("> %s\n" % command, 5)

    def log_result(self, res):
        if res == 0:
            self.logger.write("%s\n" % src.printcolors.printc(src.OK_STATUS), 5)
        else:
            self.logger.write("%s, code = %s\n" % (src.printcolors.printc(src.KO_STATUS), res), 5)

    ##
    # Logs a compilation step (configure, make ...)
    def log_step(self, step):
        if self.config.USER.output_verbose_level == 3:
            self.logger.write("\r%s%s" % (self.header, " " * 20), 3)
            self.logger.write("\r%s%s" % (self.header, step), 3)
        self.log("==== %s \n" % src.printcolors.printcInfo(step), 4)
        self.logger.flush()

    ##
    # Prepares the environment for windows.
    # Build two environment: one for building and one for testing (launch).
    def wprepare(self):
        self.log_step('PREPARE BUILD')

        if not self.build_dir.exists():
            # create build dir
            self.build_dir.make()
        elif self.options.clean_all:
            self.log('  %s\n' % src.printcolors.printcWarning("CLEAN ALL"), 4)
            # clean build dir if clean_all option given
            self.log('  clean previous build = %s\n' % str(self.build_dir), 4)
            self.build_dir.rm()
            self.build_dir.make()

        if self.options.clean_all or self.options.clean_install:
            if os.path.exists(str(self.install_dir)) and not self.single_dir:
                self.log('  clean previous install = %s\n' % str(self.install_dir), 4)
                self.install_dir.rm()

        self.log('  build_dir   = %s\n' % str(self.build_dir), 4)
        self.log('  install_dir = %s\n' % str(self.install_dir), 4)
        self.log('\n', 4)
        
        environ_info = {}
        
        # add products in depend and opt_depend list recursively
        environ_info['products'] = src.product.get_product_dependencies(self.config, self.product_info)

        # create build environment
        self.build_environ = src.environment.SalomeEnviron(self.config, src.environment.Environ(dict(os.environ)), True)
        self.build_environ.silent = (self.config.USER.output_verbose_level < 5)
        self.build_environ.set_full_environ(self.logger, environ_info)

        # create runtime environment
        self.launch_environ = src.environment.SalomeEnviron(self.config, src.environment.Environ(dict(os.environ)), False)
        self.launch_environ.silent = True # no need to show here
        self.launch_environ.set_full_environ(self.logger, environ_info)

        for ee in C_COMPILE_ENV_LIST:
            vv = self.build_environ.get(ee)
            if len(vv) > 0:
                self.log("  %s = %s\n" % (ee, vv), 4, False)

        self.results.prepare = True
        self.log_result(0)
        return self.results.prepare

    ##
    # Prepares the environment.
    # Build two environment: one for building and one for testing (launch).
    def prepare(self):
        self.log_step('PREPARE BUILD')

        if not self.build_dir.exists():
            # create build dir
            self.build_dir.make()

        self.log('  build_dir   = %s\n' % str(self.build_dir), 4)
        self.log('  install_dir = %s\n' % str(self.install_dir), 4)
        self.log('\n', 4)

        # add products in depend and opt_depend list recursively
        environ_info = src.product.get_product_dependencies(self.config, self.product_info)

        # create build environment
        self.build_environ = src.environment.SalomeEnviron(self.config, src.environment.Environ(dict(os.environ)), True)
        self.build_environ.silent = (self.config.USER.output_verbose_level < 5)
        self.build_environ.set_full_environ(self.logger, environ_info)

        # create runtime environment
        self.launch_environ = src.environment.SalomeEnviron(self.config, src.environment.Environ(dict(os.environ)), False)
        self.launch_environ.silent = True # no need to show here
        self.launch_environ.set_full_environ(self.logger, environ_info)

        for ee in C_COMPILE_ENV_LIST:
            vv = self.build_environ.get(ee)
            if len(vv) > 0:
                self.log("  %s = %s\n" % (ee, vv), 4, False)

        self.results.prepare = True
        self.log_result(0)
        return self.results.prepare

    ##
    # Runs cmake with the given options.
    def cmake(self, options=""):
        self.log_step('CMAKE')

        # cmake so no (build)configure
        self.results.configure = True

        cmake_option = options
        cmake_option +=' -DCMAKE_VERBOSE_MAKEFILE=ON -DSALOME_CMAKE_DEBUG=ON'
        if 'cmake_options' in self.product_info:
            cmake_option += " %s " % " ".join(self.product_info.cmake_options.split())

        # add debug option
        if self.debug_mode:
            cmake_option += " -DCMAKE_BUILD_TYPE=Debug"
        else :
            cmake_option += " -DCMAKE_BUILD_TYPE=Release"

        # In case CMAKE_GENERATOR is defined in environment, use it in spite of automatically detect it
        if 'cmake_generator' in self.config.APPLICATION:
            cmake_option += ' -DCMAKE_GENERATOR=%s' % self.config.PRODUCT.cmake_generator
        
        command = "cmake %s -DCMAKE_INSTALL_PREFIX=%s %s" %(cmake_option, self.install_dir, self.source_dir)

        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.results.cmake = (res == 0)
        self.log_result(res)
        return self.results.cmake

    ##
    # Runs build_configure with the given options.
    def build_configure(self, options=""):
        skip = src.get_cfg_param(self.product_info, "build_configure", False)
        if skip:
            self.results.buildconfigure = True
            res = 0
        else:
            self.log_step('BUILD CONFIGURE')

            self.results.buildconfigure = False

            if 'buildconfigure_options' in self.product_info:
                options += " %s " % self.product_info.buildconfigure_options

            command = str('./build_configure')
            command = command + " " + options
            self.log_command(command)

            res = subprocess.call(command,
                                  shell=True,
                                  cwd=str(self.source_dir),
                                  env=self.build_environ.environ.environ,
                                  stdout=self.logger.logTxtFile,
                                  stderr=subprocess.STDOUT)
            self.results.buildconfigure = (res == 0)

        self.log_result(res)
        return self.results.buildconfigure

    ##
    # Runs configure with the given options.
    def configure(self, options=""):
        self.log_step('CONFIGURE')

        # configure so no cmake
        self.results.cmake = True

        if 'configure_options' in self.product_info:
            options += " %s " % self.product_info.configure_options

        command = "%s/configure --prefix=%s" % (self.source_dir, str(self.install_dir))

        command = command + " " + options
        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.log_result(res)
        self.results.configure = (res == 0)
        return self.results.configure

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

    def get_nb_proc(self, opt_nb_proc=None):
        nbproc = -1
        if "nb_proc" in self.product_info:
            # nb proc is specified in module definition
            nbproc = self.product_info.nb_proc
            if opt_nb_proc and opt_nb_proc < self.product_info.nb_proc:
                # use command line value only if it is lower than module definition
                nbproc = opt_nb_proc
        else:
            # nb proc is not specified in module definition
            if opt_nb_proc:
                nbproc = opt_nb_proc
            else:
                nbproc = self.config.VARS.nb_proc
        
        assert nbproc > 0
        return nbproc

    ##
    # Runs make to build the module.
    def make(self, opt_nb_proc = None):
        nbproc = self.get_nb_proc(opt_nb_proc)

        hh = 'MAKE -j%s' % str(nbproc)
        if self.debug_mode:
            hh += " " + src.printcolors.printcWarning("DEBUG")
        self.log_step(hh)

        # make
        command = 'make'
        if self.options.makeflags:
            command = command + " " + self.options.makeflags
        command = command + " -j" + str(nbproc)

        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.results.make = (res == 0)
        self.log_result(res)
        return self.results.make
    
    ##
    # Runs msbuild to build the module.
    def wmake(self, opt_nb_proc = None):
        nbproc = self.get_nb_proc(opt_nb_proc)

        hh = 'MSBUILD /m:%s' % str(nbproc)
        if self.debug_mode:
            hh += " " + src.printcolors.printcWarning("DEBUG")
        self.log_step(hh)

        # make
        command = 'msbuild'
        if self.options.makeflags:
            command = command + " " + self.options.makeflags
        command = command + " /maxcpucount:" + str(nbproc)
        if self.debug_mode:
            command = command + " /p:Configuration=Debug"
        else:
            command = command + " /p:Configuration=Release"
        command = command + " ALL_BUILD.vcxproj"

        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.results.make = (res == 0)
        self.log_result(res)
        return self.results.make

    ##
    # Runs 'make install'.
    def install(self):
        self.log_step('INSTALL')
        if self.config.VARS.dist_name=="Win":
            command = 'msbuild INSTALL.vcxproj'
            if self.debug_mode:
                command = command + " /p:Configuration=Debug"
            else:
                command = command + " /p:Configuration=Release"
        else :
            command = 'make install'

        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.results.install = (res == 0)
        self.log_result(res)
        return self.results.install

    ##
    # Runs 'make_check'.
    def check(self):
        self.log_step('CHECK')
        if src.architecture.is_windows():
            command = 'msbuild RUN_TESTS.vcxproj'
        else :
            if self.use_autotools :
                command = 'make check'
            else :
                command = 'make test'
            
        self.log_command(command)

        self.results.check_tried = True
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.launch_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        self.results.check = (res == 0)
        self.log_result(res)
        return self.results.check
      
    ##
    # Performs a default build for this module.
    def do_default_build(self, build_conf_options="", configure_options="", show_warning=True):
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
            if not self.build_configure(build_conf_options): return self.get_result()
            if not self.configure(configure_options): return self.get_result()
            if not self.make(): return self.get_result()
            if not self.install(): return self.get_result()
            self.results.check = True
            if not self.clean(): return self.get_result()
           
        else: # CMake
            if self.config.VARS.dist_name=='Win':
                if not self.wprepare(): return self.get_result()
                self.results.buildconfigure = True
                if not self.cmake(): return self.get_result()
                self.results.ctest = True
                if not self.wmake(): return self.get_result()
                if not self.install(): return self.get_result()
                self.results.check = True
                if not self.clean(): return self.get_result()
            else :
                if not self.prepare(): return self.get_result()
                self.results.buildconfigure = True
                if not self.cmake(): return self.get_result()
                self.results.ctest = True
                if not self.make(): return self.get_result()
                if not self.install(): return self.get_result()
                self.results.check = True
                if not self.clean(): return self.get_result()

        return self.get_result()

    ##
    # Performs a build with a script.
    def do_script_build(self, script):
        retcode = CompilationResult()
        retcode.setAllFail()
        # script found
        self.logger.write(_("Compile %(module)s using script %(script)s\n") % \
            { 'module': self.module, 'script': src.printcolors.printcLabel(script) }, 4)
        try:
            import imp
            pymodule = imp.load_source(self.module + "_compile_script", script)
            retcode = pymodule.compil(self.config, self, self.logger)
        except:
            __, exceptionValue, exceptionTraceback = sys.exc_info()
            print(exceptionValue)
            import traceback
            traceback.print_tb(exceptionTraceback)
            traceback.print_exc()

        return retcode

    ##
    # Builds the module.
    # If a script is specified used it, else use 'default' method.
    def run_compile(self, no_compile=False):
        retcode = CompilationResult()
        retcode.setAllFail()

        if no_compile:
            if os.path.exists(str(self.install_dir)):
                retcode.setIgnored(_("already installed"))
            else:
                retcode.setIgnored(src.printcolors.printcError(_("NOT INSTALLED")))

            self.log_file.close()
            os.remove(os.path.realpath(self.log_file.name))
            return retcode

        # check if the module is already installed
        if not self.single_dir and os.path.exists(str(self.install_dir)) \
            and not self.options.clean_all and not self.options.clean_install:

            retcode.setIgnored(_("already installed"))
            self.log_file.close()
            os.remove(os.path.realpath(self.log_file.name))
            return retcode

        if 'compile_method' in self.product_info:
            if self.product_info.compile_method == "copy":
                self.prepare()
                retcode.prepare = self.results.prepare
                retcode.buildconfigure = True
                retcode.configure = True
                retcode.make = True
                retcode.cmake = True
                retcode.ctest = True
                
                if not self.source_dir.smartcopy(self.install_dir):
                    raise src.SatException(_("Error when copying %s sources to install dir") % self.module)
                retcode.install = True
                retcode.check = True

            elif self.product_info.compile_method == "default":
                retcode = self.do_default_build(show_warning=False)
                

            elif os.path.isfile(self.product_info.compile_method):
                retcode = self.do_script_build(self.product_info.compile_method)

            else:
                raise src.SatException(_("Unknown compile_method: %s") % self.product_info.compile_method)

        else:
            script = os.path.join(self.config.VARS.dataDir, 'compil_scripts', 'modules', self.module + '.py')

            if not os.path.exists(script):
                # no script use default method
                retcode = self.do_default_build(show_warning=False)
            else:
                retcode = self.do_script_build(script)

        return retcode
