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

class Builder:
    """Class to handle all construction steps, like cmake, configure, make, ...
    """
    def __init__(self, config, logger, product_info, options = src.options.OptResult(), debug_mode=False, check_src=True):
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
    def prepare(self):

        if not self.build_dir.exists():
            # create build dir
            self.build_dir.make()

        self.log('  build_dir   = %s\n' % str(self.build_dir), 4)
        self.log('  install_dir = %s\n' % str(self.install_dir), 4)
        self.log('\n', 4)

        # add products in depend and opt_depend list recursively
        environ_info = src.product.get_product_dependencies(self.config, self.product_info)
        environ_info.append(self.product_info.name)

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

        return 0

    ##
    # Runs cmake with the given options.
    def cmake(self, options=""):

        cmake_option = options
        # cmake_option +=' -DCMAKE_VERBOSE_MAKEFILE=ON -DSALOME_CMAKE_DEBUG=ON'
        if 'cmake_options' in self.product_info:
            cmake_option += " %s " % " ".join(self.product_info.cmake_options.split())

        # add debug option
        if self.debug_mode:
            cmake_option += " -DCMAKE_BUILD_TYPE=Debug"
        else :
            cmake_option += " -DCMAKE_BUILD_TYPE=Release"
        
        command = ("cmake %s -DCMAKE_INSTALL_PREFIX=%s %s" %
                            (cmake_option, self.install_dir, self.source_dir))

        self.log_command(command)
        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.build_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

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

        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs configure with the given options.
    def configure(self, options=""):

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
    def make(self, nb_proc, make_opt):

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

        if res == 0:
            return res
        else:
            return 1
    
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

        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs 'make install'.
    def install(self):
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

        if res == 0:
            return res
        else:
            return 1

    ##
    # Runs 'make_check'.
    def check(self):
        if src.architecture.is_windows():
            command = 'msbuild RUN_TESTS.vcxproj'
        else :
            if self.use_autotools :
                command = 'make check'
            else :
                command = 'make test'
            
        self.log_command(command)

        res = subprocess.call(command,
                              shell=True,
                              cwd=str(self.build_dir),
                              env=self.launch_environ.environ.environ,
                              stdout=self.logger.logTxtFile,
                              stderr=subprocess.STDOUT)

        if res == 0:
            return res
        else:
            return 1
      
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
    def do_python_script_build(self, script):
        # script found
        self.logger.write(_("Compile %(module)s using script %(script)s\n") % \
            { 'module': self.module, 'script': src.printcolors.printcLabel(script) }, 4)
        try:
            import imp
            pymodule = imp.load_source(self.product + "_compile_script", script)
            retcode = pymodule.compil(self.config, self, self.logger)
        except:
            __, exceptionValue, exceptionTraceback = sys.exc_info()
            print(exceptionValue)
            import traceback
            traceback.print_tb(exceptionTraceback)
            traceback.print_exc()

        return retcode

    def complete_environment(self, make_options):
        assert self.build_environ is not None
        # pass additional variables to environment (may be used by the build script)
        self.build_environ.set("SOURCE_DIR", str(self.source_dir))
        self.build_environ.set("INSTALL_DIR", str(self.install_dir))
        self.build_environ.set("PRODUCT_INSTALL", str(self.install_dir))
        self.build_environ.set("BUILD_DIR", str(self.build_dir))
        self.build_environ.set("PRODUCT_BUILD", str(self.build_dir))
        self.build_environ.set("MAKE_OPTIONS", make_options)
        self.build_environ.set("DIST_NAME", self.config.VARS.dist_name)
        self.build_environ.set("DIST_VERSION", self.config.VARS.dist_version)
        self.build_environ.set("DIST", self.config.VARS.dist)

    def do_batch_script_build(self, script):
        # define make options (may not be used by the script)
        nb_proc = src.get_cfg_param(self.product_info,"nb_proc", 0)
        if nb_proc == 0: 
            nb_proc = self.config.VARS.nb_proc

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

        if res == 0:
            return res
        else:
            return 1
    
    def do_script_build(self, script):
        extension = script.split('.')[-1]
        if extension in ["bat","sh"]:
            return self.do_batch_script_build(script)
        if extension == "py":
            return self.do_python_script_build(script)
        
        msg = _("The script %s must have .sh, .bat or .py extension." % script)
        raise src.SatException(msg)