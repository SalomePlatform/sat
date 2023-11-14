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
import pprint as PP
import src.debug as DBG
import src.architecture
import src.environment

def get_file_environ(output, shell, environ=None):
    """Instantiate correct FileEnvironment sub-class.
    
    :param output file: the output file stream.
    :param shell str: the type of shell syntax to use.
    :param environ dict: a potential additional environment.
    """
    if environ == None:
        environ=src.environment.Environ({})
    if shell == "bash":
        return BashFileEnviron(output, environ)
    if shell == "tcl":
        return TclFileEnviron(output, environ)
    if shell == "bat":
        return BatFileEnviron(output, environ)
    if shell == "cfgForPy":
        return LauncherFileEnviron(output, environ)
    if shell == "cfg":
        return ContextFileEnviron(output, environ)
    raise Exception("FileEnviron: Unknown shell = %s" % shell)

class FileEnviron(object):
    """\
    Base class for shell environment
    """
    def __init__(self, output, environ=None):
        """\
        Initialization
        
        :param output file: the output file stream.
        :param environ dict: SalomeEnviron.
        """
        self._do_init(output, environ)

    def __repr__(self):
        """\
        easy non exhaustive quick resume for debug print"""
        res = {
          "output" : self.output,
          "environ" : self.environ,
        }
        return "%s(\n%s\n)" % (self.__class__.__name__, PP.pformat(res))
        

    def _do_init(self, output, environ=None):
        """\
        Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self.output = output
        self.init_path=True # by default we initialise all paths, except PATH
        if environ is not None:
            self.environ = environ
        else:
            self.environ = src.environment.Environ({})

    def add_line(self, number):
        """\
        Add some empty lines in the shell file
        
        :param number int: the number of lines to add
        """
        self.output.write("\n" * number)

    def add_comment(self, comment):
        """\
        Add a comment in the shell file
        
        :param comment str: the comment to add
        """
        self.output.write("# %s\n" % comment)

    def add_echo(self, text):
        """\
        Add a "echo" in the shell file
        
        :param text str: the text to echo
        """
        self.output.write('echo %s"\n' % text)

    def add_warning(self, warning):
        """\
        Add a warning "echo" in the shell file
        
        :param warning str: the text to echo
        """
        self.output.write('echo "WARNING %s"\n' % warning)

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
            raise Exception("FileEnviron append key '%s' value '%s' contains forbidden character '%s'" % (key, value, separator))
        do_append=True
        if self.environ.is_defined(key):
            value_list = self.environ.get(key).split(sep)
            if self.environ._expandvars(value) in value_list:
                do_append=False  # value is already in key path : we don't append it again
            
        if do_append:
            self.environ.append_value(key, value,sep)
            self.set(key, self.get(key) + sep + value)

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
            raise Exception("FileEnviron append key '%s' value '%s' contains forbidden character '%s'" % (key, value, separator))

        do_not_prepend=False
        if self.environ.is_defined(key):
            value_list = self.environ.get(key).split(sep)
            exp_val=self.environ._expandvars(value)
            if exp_val in value_list:
                do_not_prepend=True
        if not do_not_prepend:
            self.environ.prepend_value(key, value,sep)
            self.set(key, value + sep + self.get(key))

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
        return self.environ.is_defined(key)

    def set(self, key, value):
        """\
        Set the environment variable 'key' to value 'value'
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        raise NotImplementedError("set is not implement for this shell!")

    def get(self, key):
        """\
        Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        if src.architecture.is_windows():
            return '%' + key + '%'
        else:
            return '${%s}' % key

    def get_value(self, key):
        """Get the real value of the environment variable "key"
        It can help env scripts
        :param key str: the environment variable
        """
        return self.environ.get_value(key)

    def finish(self):
        """Add a final instruction in the out file (in case of file generation)
        
        :param required bool: Do nothing if required is False
        """
        return

    def set_no_init_path(self):
        """Set the no initialisation mode for all paths.
           By default only PATH is not reinitialised. All others paths are
           (LD_LIBRARY_PATH, PYTHONPATH, ...)
           After the call to these function ALL PATHS ARE NOT REINITIALISED.
           There initial value is inherited from the environment
        """
        self.init_path=False

    def value_filter(self, value):
        res=value
        return res


class TclFileEnviron(FileEnviron):
    """\
    Class for tcl shell.
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.output.write(tcl_header.replace("<module_name>",
                                             self.environ.get("sat_product_name")))
        self.output.write("\nset software %s\n" % self.environ.get("sat_product_name") )
        self.output.write("set version %s\n" % self.environ.get("sat_product_version") )
        root=os.path.join(self.environ.get("sat_product_base_path"),  
                                  "apps", 
                                  self.environ.get("sat_product_base_name"), 
                                  "$software", 
                                  "$version")
        self.output.write("set root %s\n" % root) 
        modules_to_load=self.environ.get("sat_product_load_depend")
        if len(modules_to_load)>0:
            # write module load commands for product dependencies
            self.output.write("\n")
            for module_to_load in modules_to_load.split(";"):
                self.output.write(module_to_load+"\n")

    def set(self, key, value):
        """Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.output.write('setenv  %s "%s"\n' % (key, value))
        self.environ.set(key, value)
        
    def get(self, key):
        """\
        Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        return self.environ.get(key)

    def append_value(self, key, value, sep=os.pathsep):
        """append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        """
        if sep==os.pathsep:
            self.output.write('append-path  %s   %s\n' % (key, value))
        else:
            self.output.write('append-path --delim=\%c %s   %s\n' % (sep, key, value))

    def prepend_value(self, key, value, sep=os.pathsep):
        """prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        if sep==os.pathsep:
            self.output.write('prepend-path  %s   %s\n' % (key, value))
        else:
            self.output.write('prepend-path --delim=\%c %s   %s\n' % (sep, key, value))

        
class BashFileEnviron(FileEnviron):
    """\
    Class for bash shell.
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.output.write(bash_header)

    def set(self, key, value):
        """Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.output.write('export %s="%s"\n' % (key, value))
        self.environ.set(key, value)
        

        
class BatFileEnviron(FileEnviron):
    """\
    for Windows batch shell.
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.output.write(bat_header)

    def add_comment(self, comment):
        """Add a comment in the shell file
        
        :param comment str: the comment to add
        """
        self.output.write("rem %s\n" % comment)
    
    def get(self, key):
        """Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        return '%%%s%%' % key
    
    def set(self, key, value):
        """Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.output.write('set %s=%s\n' % (key, self.value_filter(value)))
        self.environ.set(key, value)


class ContextFileEnviron(FileEnviron):
    """Class for a salome context configuration file.
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.output.write(cfg_header)

    def set(self, key, value):
        """Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.output.write('%s="%s"\n' % (key, value))
        self.environ.set(key, value)

    def get(self, key):
        """Get the value of the environment variable "key"
        
        :param key str: the environment variable
        """
        return '%({0})s'.format(key)

    def add_echo(self, text):
        """Add a comment
        
        :param text str: the comment to add
        """
        self.add_comment(text)

    def add_warning(self, warning):
        """Add a warning
        
        :param text str: the warning to add
        """
        self.add_comment("WARNING %s"  % warning)

    def prepend_value(self, key, value, sep=os.pathsep):
        """prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        do_append=True
        if self.environ.is_defined(key):
            value_list = self.environ.get(key).split(sep)
            #value cannot be expanded (unlike bash/bat case) - but it doesn't matter.
            if value in value_list:
                do_append=False  # value is already in key path : we don't append it again
            
        if do_append:
            self.environ.append_value(key, value,sep)
            self.output.write('ADD_TO_%s: %s\n' % (key, value))

    def append_value(self, key, value, sep=os.pathsep):
        """append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        """
        self.prepend_value(key, value)


class LauncherFileEnviron(FileEnviron):
    """\
    Class to generate a launcher file script 
    (in python syntax) SalomeContext API
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.python_version=self.environ.get("sat_python_version")
        self.bin_kernel_root_dir=self.environ.get("sat_bin_kernel_install_dir")

        # four whitespaces for first indentation in a python script
        self.indent="    "
        self.prefix="context."
        self.setVarEnv="setVariable"
        self.begin=self.indent+self.prefix

        # write the begining of launcher file.
        # choose the template version corresponding to python version 
        # and substitute BIN_KERNEL_INSTALL_DIR (the path to salomeContext.py)
        if self.python_version == 2:
            launcher_header=launcher_header2
        else:
            launcher_header=launcher_header3
        # in case of Windows OS, Python scripts are not executable.  PyExe ?
        if src.architecture.is_windows():
            launcher_header = launcher_header.replace("#! /usr/bin/env python3",'')
        self.output.write(launcher_header\
                          .replace("BIN_KERNEL_INSTALL_DIR", self.bin_kernel_root_dir))

        # for these path, we use specialired functions in salomeContext api
        self.specialKeys={"PATH": "Path",
                          "LD_LIBRARY_PATH": "LdLibraryPath",
                          "PYTHONPATH": "PythonPath"}

        # we do not want to reinitialise PATH.
        # for that we make sure PATH is in self.environ
        # and therefore we will not use setVariable for PATH
        if not self.environ.is_defined("PATH"):
            self.environ.set("PATH","")

    def add_echo(self, text):
        """Add a comment
        
        :param text str: the comment to add
        """
        self.output.write('# %s"\n' % text)

    def add_warning(self, warning):
        """Add a warning
        
        :param text str: the warning to add
        """
        self.output.write('# "WARNING %s"\n' % warning)

    def append_value(self, key, value, sep=os.pathsep):
        """append value to key using sep,
        if value contains ":" or ";" then raise error
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        # check that value so no contain the system separator
        separator=os.pathsep
        msg="LauncherFileEnviron append key '%s' value '%s' contains forbidden character '%s'"
        if separator in value:
            raise Exception(msg % (key, value, separator))

        is_key_defined=self.environ.is_defined(key)
        conditional_reinit=False
        if (self.init_path and (not is_key_defined)):
            # reinitialisation mode set to true (the default)
            # for the first occurrence of key, we set it.
            # therefore key will not be inherited from environment
            self.output.write(self.indent+'if reinitialise_paths:\n'+self.indent)
            self.set(key, value)
            self.output.write(self.indent+'else:\n'+self.indent)
            conditional_reinit=True # in this case do not register value in self.environ a second time

        # in all other cases we use append (except if value is already the key
        do_append=True
        if is_key_defined:
            value_list = self.environ.get(key).split(sep)
            # rem : value cannot be expanded (unlike bash/bat case) - but it doesn't matter.
            if value in value_list:
                do_append=False  # value is already in key path : we don't append it again
            
        if do_append:
            if not conditional_reinit:
                self.environ.append_value(key, value,sep) # register value in self.environ
            if key in self.specialKeys.keys():
                #for these special keys we use the specific salomeContext function
                self.output.write(self.begin+'addTo%s(r"%s")\n' % 
                                  (self.specialKeys[key], self.value_filter(value)))
            else:
                # else we use the general salomeContext addToVariable function
                self.output.write(self.begin+'appendVariable(r"%s", r"%s",separator="%s")\n'
                                  % (key, self.value_filter(value), sep))

    def append(self, key, value, sep=":"):
        """Same as append_value but the value argument can be a list
        
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
        """prepend value to key using sep,
        if value contains ":" or ";" then raise error
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        """
        # check that value so no contain the system separator
        separator=os.pathsep
        msg="LauncherFileEnviron append key '%s' value '%s' contains forbidden character '%s'"
        if separator in value:
            raise Exception(msg % (key, value, separator))

        is_key_defined=self.environ.is_defined(key)
        conditional_reinit=False
        if (self.init_path and (not is_key_defined)):
            # reinitialisation mode set to true (the default)
            # for the first occurrence of key, we set it.
            # therefore key will not be inherited from environment
            self.output.write(self.indent+'if reinitialise_paths:\n'+self.indent)
            self.set(key, value)
            self.output.write(self.indent+'else:\n'+self.indent)
            conditional_reinit=True # in this case do not register value in self.environ a second time

        # in all other cases we use append (except if value is already the key
        do_append=True
        if is_key_defined:
            value_list = self.environ.get(key).split(sep)
            # rem : value cannot be expanded (unlike bash/bat case) - but it doesn't matter.
            if value in value_list:
                do_append=False  # value is already in key path : we don't append it again
            
        if do_append:
            if not conditional_reinit:
                self.environ.append_value(key, value,sep) # register value in self.environ
            if key in self.specialKeys.keys():
                #for these special keys we use the specific salomeContext function
                self.output.write(self.begin+'addTo%s(r"%s")\n' % 
                                  (self.specialKeys[key], self.value_filter(value)))
            else:
                # else we use the general salomeContext addToVariable function
                self.output.write(self.begin+'addToVariable(r"%s", r"%s",separator="%s")\n' 
                                  % (key, self.value_filter(value), sep))
            

    def prepend(self, key, value, sep=":"):
        """Same as prepend_value but the value argument can be a list
        
        :param key str: the environment variable to prepend
        :param value str or list: the value(s) to prepend to key
        :param sep str: the separator string
        """
        if isinstance(value, list):
            for v in value:
                self.prepend_value(key, v, sep)
        else:
            self.prepend_value(key, value, sep)


    def set(self, key, value):
        """Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        """
        self.output.write(self.begin+self.setVarEnv+
                          '(r"%s", r"%s", overwrite=True)\n' % 
                          (key, self.value_filter(value)))
        self.environ.set(key,value)
    

    def add_comment(self, comment):
        # Special comment in case of the DISTENE licence
        if comment=="DISTENE license":
            self.output.write(self.indent+
                              "#"+
                              self.prefix+
                              self.setVarEnv+
                              '(r"%s", r"%s", overwrite=True)\n' % 
                              ('DISTENE_LICENSE_FILE', 'Use global envvar: DLIM8VAR'))
            self.output.write(self.indent+
                              "#"+
                              self.prefix+
                              self.setVarEnv+
                              '(r"%s", r"%s", overwrite=True)\n' % 
                              ('DLIM8VAR', '<your licence>'))
            return
        if "setting environ for" in comment:
            self.output.write(self.indent+"#[%s]\n" % 
                              comment.split("setting environ for ")[1])
            return

        self.output.write(self.indent+"# %s\n" % comment)

    def finish(self):
        """\
        Add a final instruction in the out file (in case of file generation)
        In the particular launcher case, do nothing
        
        :param required bool: Do nothing if required is False
        """
        if self.python_version == 2:
            launcher_tail=launcher_tail_py2
        else:
            launcher_tail=launcher_tail_py3
        self.output.write(launcher_tail)
        return

class ScreenEnviron(FileEnviron):
    def __init__(self, output, environ=None):
        self._do_init(output, environ)
        self.defined = {}

    def add_line(self, number):
        pass

    def add_comment(self, comment):
        pass

    def add_echo(self, text):
        pass

    def add_warning(self, warning):
        pass

    def write(self, command, name, value, sign="="):
        import src
        self.output.write("  %s%s %s %s %s\n" % \
            (src.printcolors.printcLabel(command),
             " " * (12 - len(command)),
             src.printcolors.printcInfo(name), sign, value))

    def is_defined(self, name):
        return name in self.defined

    def get(self, name):
        return "${%s}" % name

    def set(self, name, value):
        self.write("set", name, value)
        self.defined[name] = value

    def prepend(self, name, value, sep=":"):
        if isinstance(value, list):
            value = sep.join(value)
        value = value + sep + self.get(name)
        self.write("prepend", name, value)

    def append(self, name, value, sep=":"):
        if isinstance(value, list):
            value = sep.join(value)
        value = self.get(name) + sep + value
        self.write("append", name, value)

    def run_env_script(self, module, script):
        self.write("load", script, "", sign="")


#
#  Headers
#
bat_header="""\
@echo off

rem The following variables are used only in case of a sat package
set out_dir_Path=%~dp0
"""

tcl_header="""\
#%Module -*- tcl -*-
#
# <module_name> module for use with 'environment-modules' package
#
"""

bash_header="""\
#!/bin/bash
if [ "$BASH" = "" ]
then
  # check that the user is not using another shell
  echo
  echo "Warning! SALOME environment not initialized"
  echo "You must run this script in a bash shell."
  echo "As you are using another shell. Please first run: bash"
  echo
fi
##########################################################################
#
# This line is used only in case of a sat package
export out_dir_Path=$(cd $(dirname ${BASH_SOURCE[0]});pwd)

###########################################################################
"""

cfg_header="""\
[SALOME Configuration]
"""

launcher_header2="""\
#! /usr/bin/env python

################################################################
# WARNING: this file is automatically generated by SalomeTools #
# WARNING: and so could be overwritten at any time.            #
################################################################

import os
import sys
import subprocess
import os.path

# Add the pwdPath to able to run the launcher after unpacking a package
# Used only in case of a salomeTools package
out_dir_Path=os.path.dirname(os.path.realpath(__file__))

# Preliminary work to initialize path to SALOME Python modules
def __initialize():

  sys.path[:0] = [ r'BIN_KERNEL_INSTALL_DIR' ]  # to get salomeContext
  
  # define folder to store omniorb config (initially in virtual application folder)
  try:
    from salomeContextUtils import setOmniOrbUserPath
    setOmniOrbUserPath()
  except Exception as e:
    print(e)
    sys.exit(1)
# End of preliminary work

# salome doc only works for virtual applications. Therefore we overwrite it with this function
def _showDoc(modules):
    for module in modules:
      modulePath = os.getenv(module+"_ROOT_DIR")
      if modulePath != None:
        baseDir = os.path.join(modulePath, "share", "doc", "salome")
        docfile = os.path.join(baseDir, "gui", module.upper(), "index.html")
        if not os.path.isfile(docfile):
          docfile = os.path.join(baseDir, "tui", module.upper(), "index.html")
        if not os.path.isfile(docfile):
          docfile = os.path.join(baseDir, "dev", module.upper(), "index.html")
        if os.path.isfile(docfile):
          out, err = subprocess.Popen(["xdg-open", docfile]).communicate()
        else:
          print ("Online documentation is not accessible for module:", module)
      else:
        print (module+"_ROOT_DIR not found!")

def main(args):
  # Identify application path then locate configuration files
  __initialize()

  if args == ['--help']:
    from salomeContext import usage
    usage()
    sys.exit(0)


  # Create a SalomeContext which parses configFileNames to initialize environment
  try:
    from salomeContext import SalomeContext, SalomeContextException
    if 'appendVariable' not in dir(SalomeContext):
      # check whether the appendVariable method is implemented
      def appendVariable(self, name, value, separator=os.pathsep):
        if value == '':
          return
        value = os.path.expandvars(value) # expand environment variables
        env = os.getenv(name, None)
        if env is None:
          os.environ[name] = value
        else:
          os.environ[name] = env + separator + value
        return
      SalomeContext.appendVariable = appendVariable

    context = SalomeContext(None)

    # Here set specific variables, if needed
    # context.addToPath('mypath')
    # context.addToLdLibraryPath('myldlibrarypath')
    # context.addToPythonPath('mypythonpath')
    # context.setVariable('myvarname', 'value')

    # Logger level error
    context.getLogger().setLevel(40)
"""

launcher_header3="""\
#! /usr/bin/env python3

################################################################
# WARNING: this file is automatically generated by SalomeTools #
# WARNING: and so could be overwritten at any time.            #
################################################################

import os
import sys
import subprocess
import os.path

# Add the pwdPath to able to run the launcher after unpacking a package
# Used only in case of a salomeTools package
out_dir_Path=os.path.dirname(os.path.realpath(__file__))

# Preliminary work to initialize path to SALOME Python modules
def __initialize():

  sys.path[:0] = [ r'BIN_KERNEL_INSTALL_DIR' ]
  
  # define folder to store omniorb config (initially in virtual application folder)
  try:
    from salomeContextUtils import setOmniOrbUserPath
    setOmniOrbUserPath()
  except Exception as e:
    print(e)
    sys.exit(1)
# End of preliminary work

# salome doc only works for virtual applications. Therefore we overwrite it with this function
def _showDoc(modules):
    for module in modules:
      modulePath = os.getenv(module+"_ROOT_DIR")
      if modulePath != None:
        baseDir = os.path.join(modulePath, "share", "doc", "salome")
        docfile = os.path.join(baseDir, "gui", module.upper(), "index.html")
        if not os.path.isfile(docfile):
          docfile = os.path.join(baseDir, "tui", module.upper(), "index.html")
        if not os.path.isfile(docfile):
          docfile = os.path.join(baseDir, "dev", module.upper(), "index.html")
        if os.path.isfile(docfile):
          out, err = subprocess.Popen(["xdg-open", docfile]).communicate()
        else:
          print("Online documentation is not accessible for module:", module)
      else:
        print(module+"_ROOT_DIR not found!")

def main(args):
  # Identify application path then locate configuration files
  __initialize()

  if '--help' in args:
    from salomeContext import usage
    usage()
    sys.exit(0)

  reinitialise_paths=True
  if '--keep-paths' in args:
    reinitialise_paths=False
    args.remove('--keep-paths')

  #from salomeContextUtils import getConfigFileNames
  #configFileNames, args, unexisting = getConfigFileNames( args, checkExistence=True )
  #if len(unexisting) > 0:
  #  print("ERROR: unexisting configuration file(s): " + ', '.join(unexisting))
  #  sys.exit(1)

  # Create a SalomeContext which parses configFileNames to initialize environment
  try:
    from salomeContext import SalomeContext, SalomeContextException
    if 'appendVariable' not in dir(SalomeContext):
      # check whether the appendVariable method is implemented
      def appendVariable(self, name, value, separator=os.pathsep):
        if value == '':
          return
        value = os.path.expandvars(value) # expand environment variables
        env = os.getenv(name, None)
        if env is None:
          os.environ[name] = value
        else:
          os.environ[name] = env + separator + value
        return
      SalomeContext.appendVariable = appendVariable

    context = SalomeContext(None)
    # Here set specific variables, if needed
    # context.addToPath('mypath')
    # context.addToLdLibraryPath('myldlibrarypath')
    # context.addToPythonPath('mypythonpath')
    # context.setVariable('myvarname', 'value')

    # Logger level error
    context.getLogger().setLevel(40)
"""

launcher_tail_py2="""\
    #[hook to integrate in launcher additionnal user modules]
    
    # Load all files extra.env.d/*.py and call the module's init routine]

    extradir=out_dir_Path + r"/extra.env.d"

    if os.path.exists(extradir):
        import imp
        sys.path.insert(0, os.path.join(os.getcwd(), extradir))
        for filename in sorted(
            filter(lambda x: os.path.isfile(os.path.join(extradir, x)),
                   os.listdir(extradir))):

            if filename.endswith(".py"):
                f = os.path.join(extradir, filename)
                module_name = os.path.splitext(os.path.basename(f))[0]
                fp, path, desc = imp.find_module(module_name)
                module = imp.load_module(module_name, fp, path, desc)
                module.init(context, out_dir_Path)

    #[manage salome doc command]
    if len(args) >1 and args[0]=='doc':
        _showDoc(args[1:])
        return

    # Start SALOME, parsing command line arguments
    out, err, status = context.runSalome(args)
    sys.exit(status)

  except SalomeContextException, e:
    import logging
    logging.getLogger("salome").error(e)
    sys.exit(1)

if __name__ == "__main__":
  args = sys.argv[1:]
  main(args)
#
"""

launcher_tail_py3="""\
    #[hook to integrate in launcher additionnal user modules]
    
    # Load all files extra.env.d/*.py and call the module's init routine]

    extradir=out_dir_Path + r"/extra.env.d"

    if os.path.exists(extradir):
        import importlib
        import importlib.util
        sys.path.insert(0, os.path.join(os.getcwd(), extradir))
        for filename in sorted(
            filter(lambda x: os.path.isfile(os.path.join(extradir, x)),
                   os.listdir(extradir))):

            if filename.endswith(".py"):
                f = os.path.join(extradir, filename)
                module_name = os.path.splitext(os.path.basename(f))[0]
                _specs = importlib.util.find_spec(module_name)
                _module = importlib.util.module_from_spec(_specs)
                _specs.loader.exec_module(_module)
                _module.init(context, out_dir_Path)
    #[manage salome doc command]
    if len(args) >1 and args[0]=='doc':
        _showDoc(args[1:])
        return

    # Start SALOME, parsing command line arguments
    out, err, status = context.runSalome(args)
    sys.exit(status)

  except SalomeContextException as e:
    import logging
    logging.getLogger("salome").error(e)
    sys.exit(1)
 

if __name__ == "__main__":
  args = sys.argv[1:]
  main(args)
#
"""
    

