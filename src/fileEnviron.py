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

bat_header="""@echo off

rem The following variables are used only in case of a sat package
set out_dir_Path=%~dp0
set PRODUCT_OUT_DIR=%out_dir_Path%
set prereq_install_Path=%out_dir_Path%\PREREQUISITES\INSTALL
set prereq_build_Path=%out_dir_Path%\PREREQUISITES\BUILD
"""


bash_header="""#!/bin/bash
##########################################################################
#
#### cleandup ###
# cleanup a path (first parameter) from duplicated entries;
# second parameter is the separator
cleandup() {
out_var=`echo $1 | awk -v sep=$2 '{                      \\
     na = split($1,a,sep);                               \\
     k=0;                                                \\
     for(i=0;i<=na;i++) {                                \\
       found=0;                                          \\
       for(j=0;j<k;j++) {                                \\
         if(a[i]==aa[j])                                 \\
         {                                               \\
           found=1;                                      \\
           break;                                        \\
         };                                              \\
       };                                                \\
       if(found==0) {                                    \\
         aa[k++]=a[i];                                   \\
       };                                                \\
     };                                                  \\
     ORS=sep;                                            \\
     for(i=0;i<k;i++) {                                  \\
       print aa[i];                                      \\
     }                                                   \\
   }' | sed -e 's|\\(.*\\)$1|\\1|g' -e 's|^[:;]||' -e 's|[:;]$||'`
echo $out_var
}
### clean ###
clean ()
{
xenv=`printenv $1`
out_var=`cleandup $xenv $2`
export $1=$out_var
}

# The 3 following variables are used only in case of a sat package
export out_dir_Path=`dirname "${BASH_SOURCE[0]}"`
export PRODUCT_OUT_DIR=${out_dir_Path}
export PRODUCT_ROOT_DIR=${PRODUCT_OUT_DIR}

###########################################################################
"""


Launcher_header='''# a generated SALOME Configuration file using python syntax
'''

def get_file_environ(output, shell, environ=None):
    """Instantiate correct FileEnvironment sub-class.
    
    :param output file: the output file stream.
    :param shell str: the type of shell syntax to use.
    :param environ dict: a potential additional environment.
    """
    if shell == "bash":
        return BashFileEnviron(output, environ)
    if shell == "bat":
        return BatFileEnviron(output, environ)
    if shell == "cfgForPy":
        return LauncherFileEnviron(output, environ)
    raise Exception("FileEnviron: Unknown shell = %s" % shell)

class FileEnviron:
    """Base class for shell environment
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)

    def _do_init(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self.output = output
        self.toclean = []
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ

    def add_line(self, number):
        """Add some empty lines in the shell file
        
        :param number int: the number of lines to add
        """
        self.output.write("\n" * number)

    def add_comment(self, comment):
        """Add a comment in the shell file
        
        :param comment str: the comment to add
        """
        self.output.write("# %s\n" % comment)

    def add_echo(self, text):
        """Add a "echo" in the shell file
        
        :param text str: the text to echo
        """
        self.output.write('echo %s"\n' % text)

    def add_warning(self, warning):
        """Add a warning "echo" in the shell file
        
        :param warning str: the text to echo
        """
        self.output.write('echo "WARNING %s"\n' % warning)

    def append_value(self, key, value, sep=os.pathsep):
        '''append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        '''
        self.set(key, self.get(key) + sep + value)
        if (key, sep) not in self.toclean:
            self.toclean.append((key, sep))

    def append(self, key, value, sep=os.pathsep):
        '''Same as append_value but the value argument can be a list
        
        :param key str: the environment variable to append
        :param value str or list: the value(s) to append to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            self.append_value(key, sep.join(value), sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=os.pathsep):
        '''prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        '''
        self.set(key, value + sep + self.get(key))
        if (key, sep) not in self.toclean:
            self.toclean.append((key, sep))

    def prepend(self, key, value, sep=os.pathsep):
        '''Same as prepend_value but the value argument can be a list
        
        :param key str: the environment variable to prepend
        :param value str or list: the value(s) to prepend to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            self.prepend_value(key, sep.join(value), sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        '''Check if the key exists in the environment
        
        :param key str: the environment variable to check
        '''
        return (key in self.environ)

    def set(self, key, value):
        '''Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        '''
        raise NotImplementedError("set is not implement for this shell!")

    def get(self, key):
        '''Get the value of the environment variable "key"
        
        :param key str: the environment variable
        '''
        return '${%s}' % key

    def command_value(self, key, command):
        '''Get the value given by the system command "command" 
           and put it in the environment variable key.
           Has to be overwritten in the derived classes
           This can be seen as a virtual method
        
        :param key str: the environment variable
        :param command str: the command to execute
        '''
        raise NotImplementedError("command_value is not implement "
                                  "for this shell!")

    def finish(self, required=True):
        """Add a final instruction in the out file (in case of file generation)
        
        :param required bool: Do nothing if required is False
        """
        for (key, sep) in self.toclean:
            if sep != ' ':
                self.output.write('clean %s "%s"\n' % (key, sep))

class BashFileEnviron(FileEnviron):
    """Class for bash shell.
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self._do_init(output, environ)
        self.output.write(bash_header)

    def set(self, key, value):
        '''Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        '''
        self.output.write('export %s="%s"\n' % (key, value))
        self.environ[key] = value

    def command_value(self, key, command):
        '''Get the value given by the system command "command" 
           and put it in the environment variable key.
           Has to be overwritten in the derived classes
           This can be seen as a virtual method
        
        :param key str: the environment variable
        :param command str: the command to execute
        '''
        self.output.write('export %s=$(%s)\n' % (key, command))

    def finish(self, required=True):
        """Add a final instruction in the out file (in case of file generation)
        
        :param required bool: Do nothing if required is False
        """
        if not required:
            return
        FileEnviron.finish(self, required)
        
class BatFileEnviron(FileEnviron):
    """for Windows batch shell.
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
        '''Get the value of the environment variable "key"
        
        :param key str: the environment variable
        '''
        return '%%%s%%' % key
    
    def set(self, key, value):
        '''Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        '''
        self.output.write('set %s=%s\n' % (key, value))
        self.environ[key] = value

    def command_value(self, key, command):
        '''Get the value given by the system command "command" 
           and put it in the environment variable key.
           Has to be overwritten in the derived classes
           This can be seen as a virtual method
        
        :param key str: the environment variable
        :param command str: the command to execute
        '''
        self.output.write('%s > tmp.txt\n' % (command))
        self.output.write('set /p %s =< tmp.txt\n' % (key))

    def finish(self, required=True):
        """Add a final instruction in the out file (in case of file generation)
           In the particular windows case, do nothing
        
        :param required bool: Do nothing if required is False
        """
        return

def special_path_separator(name):
    """TCLLIBPATH, TKLIBPATH, PV_PLUGIN_PATH environments variables need
       some exotic path separator.
       This function gives the separator regarding the name of the variable
       to append or prepend.
       
    :param name str: The name of the variable to find the separator
    """
    special_blanks_keys=["TCLLIBPATH", "TKLIBPATH"]
    special_semicolon_keys=["PV_PLUGIN_PATH"]
    res=os.pathsep
    if name in special_blanks_keys: res=" "
    if name in special_semicolon_keys: res=";"
    return res

class LauncherFileEnviron:
    """Class to generate a launcher file script 
       (in python syntax) SalomeContext API
    """
    def __init__(self, output, environ=None):
        """Initialization
        
        :param output file: the output file stream.
        :param environ dict: a potential additional environment.
        """
        self.output = output
        self.toclean = []
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ
        # Initialize some variables
        if not "PATH" in self.environ.keys():
            self.environ["PATH"]=""
        if not "LD_LIBRARY_PATH" in self.environ.keys():
            self.environ["LD_LIBRARY_PATH"]=""
        if not "PYTHONPATH" in self.environ.keys():
            self.environ["PYTHONPATH"]=""
        if not "TCLLIBPATH" in self.environ.keys():
            self.environ["TCLLIBPATH"]=""
        if not "TKLIBPATH" in self.environ.keys():
            self.environ["TKLIBPATH"]=""

        # four whitespaces for first indentation in a python script
        self.indent="    "
        self.prefix="context."
        self.setVarEnv="setVariable"
        
        self.begin=self.indent+self.prefix
        self.output.write(Launcher_header)
        self.specialKeys={"PATH": "Path",
                          "LD_LIBRARY_PATH": "LdLibraryPath",
                          "PYTHONPATH": "PythonPath"}

    def change_to_launcher(self, value):
        """
        """
        res=value
        return res

    def add_line(self, number):
        """Add some empty lines in the launcher file
        
        :param number int: the number of lines to add
        """
        self.output.write("\n" * number)

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

    def append_value(self, key, value, sep=":"):
        '''append value to key using sep
        
        :param key str: the environment variable to append
        :param value str: the value to append to key
        :param sep str: the separator string
        '''
        if self.is_defined(key) :
            self.add(key, value)
        else :
            self.set(key, value)

    def append(self, key, value, sep=":"):
        '''Same as append_value but the value argument can be a list
        
        :param key str: the environment variable to append
        :param value str or list: the value(s) to append to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            self.append_value(key, sep.join(value), sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=":"):
        '''prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        :param sep str: the separator string
        '''
        if self.is_defined(key) :
            self.add(key, value)
        else :
            self.set(key, value)

    def prepend(self, key, value, sep=":"):
        '''Same as prepend_value but the value argument can be a list
        
        :param key str: the environment variable to prepend
        :param value str or list: the value(s) to prepend to key
        :param sep str: the separator string
        '''
        if isinstance(value, list):
            self.prepend_value(key, sep.join(value), sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        '''Check if the key exists in the environment
        
        :param key str: the environment variable to check
        '''
        return key in self.environ.keys()

    def get(self, key):
        '''Get the value of the environment variable "key"
        
        :param key str: the environment variable
        '''
        return '${%s}' % key

    def set(self, key, value):
        '''Set the environment variable "key" to value "value"
        
        :param key str: the environment variable to set
        :param value str: the value
        '''
        self.output.write(self.begin+self.setVarEnv+
                          '(r"%s", r"%s", overwrite=True)\n' % 
                          (key, self.change_to_launcher(value)))
        self.environ[key] = value
    
    def add(self, key, value):
        '''prepend value to key using sep
        
        :param key str: the environment variable to prepend
        :param value str: the value to prepend to key
        '''     
        if key in self.specialKeys.keys():
            self.output.write(self.begin+'addTo%s(r"%s")\n' % 
                              (self.specialKeys[key],
                               self.change_to_launcher(value)))
            self.environ[key]+=":"+value
            return
        sep=special_path_separator(key)
        self.output.write(self.indent+
                          '#temporary solution!!! have to be defined in API a '
                          '?dangerous? addToSpecial(r"%s", r"%s")\n' % 
                          (key, value))
        #pathsep not precised because do not know future os launch?
        self.output.write(self.begin+'addToSpecial(r"%s", r"%s")\n' 
                          % (key, self.change_to_launcher(value)))
        self.environ[key]+=sep+value #here yes we know os for current execution

    def command_value(self, key, command):
        '''Get the value given by the system command "command" 
           and put it in the environment variable key.
        
        :param key str: the environment variable
        :param command str: the command to execute
        '''
        self.output.write(self.indent+'#`%s`\n' % command)

        import shlex, subprocess
        args = shlex.split(command)
        res=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, __ = res.communicate()
        self.output.write(self.begin+
                          self.setVarEnv+
                          '(r"%s", r"%s", overwrite=True)\n' % (key, out))

    def add_comment(self, comment):
        # Special comment in case of the distène licence
        if comment=="DISTENE license":
            self.output.write(self.indent+
                              "#"+
                              self.prefix+
                              self.setVarEnv+
                              '(r"%s", r"%s", overwrite=True)\n' % 
                              ('DISTENE_LICENSE_FILE', 
                               self.change_to_launcher(
                                            'Use global envvar: DLIM8VAR')))
            self.output.write(self.indent+
                              "#"+
                              self.prefix+
                              self.setVarEnv+
                              '(r"%s", r"%s", overwrite=True)\n' % 
                              ('DLIM8VAR', 
                               self.change_to_launcher(
                                                '<your licence>')))
            return
        if "setting environ for" in comment:
            self.output.write(self.indent+"#[%s]\n" % 
                              comment.split("setting environ for ")[1])
            return

        self.output.write(self.indent+"# %s\n" % comment)

    def finish(self, required=True):
        """Add a final instruction in the out file (in case of file generation)
           In the particular launcher case, do nothing
        
        :param required bool: Do nothing if required is False
        """
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
        return self.defined.has_key(name)

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

    def command_value(self, key, command):
        pass

    def run_env_script(self, module, script):
        self.write("load", script, "", sign="")

# The SALOME launcher template 
withProfile =  """#! /usr/bin/env python

################################################################
# WARNING: this file is automatically generated by SalomeTools #
# WARNING: and so could be overwritten at any time.            #
################################################################

import os
import sys


# Add the pwdPath to able to run the launcher after unpacking a package
# Used only in case of a salomeTools package
out_dir_Path=os.path.abspath(os.path.dirname(__file__))

# Preliminary work to initialize path to SALOME Python modules
def __initialize():

  sys.path[:0] = [ os.path.join( 'PROFILE_INSTALL_DIR', 'bin', 'salome' ) ]
  os.environ['ABSOLUTE_APPLI_PATH'] = 'PROFILE_INSTALL_DIR'
  
  # define folder to store omniorb config (initially in virtual application folder)
  try:
    from salomeContextUtils import setOmniOrbUserPath
    setOmniOrbUserPath()
  except Exception, e:
    print e
    sys.exit(1)
# End of preliminary work

def main(args):
  # Identify application path then locate configuration files
  __initialize()

  if args == ['--help']:
    from salomeContext import usage
    usage()
    sys.exit(0)

  #from salomeContextUtils import getConfigFileNames
  #configFileNames, args, unexisting = getConfigFileNames( args, checkExistence=True )
  #if len(unexisting) > 0:
  #  print "ERROR: unexisting configuration file(s): " + ', '.join(unexisting)
  #  sys.exit(1)

  # Create a SalomeContext which parses configFileNames to initialize environment
  try:
    from salomeContext import SalomeContext, SalomeContextException
    SalomeContext.addToSpecial=addToSpecial
    context = SalomeContext(None)
    
    # Here set specific variables, if needed
    # context.addToPath('mypath')
    # context.addToLdLibraryPath('myldlibrarypath')
    # context.addToPythonPath('mypythonpath')
    # context.setVariable('myvarname', 'value')

    # Logger level error
    context.getLogger().setLevel(40)

    context.setVariable(r"PRODUCT_ROOT_DIR", out_dir_Path, overwrite=True)
    # here your local standalone environment

    # Start SALOME, parsing command line arguments
    context.runSalome(args)
    #print 'Thank you for using SALOME!'

    # Logger level info
    context.getLogger().setLevel(20)

  except SalomeContextException, e:
    import logging
    logging.getLogger("salome").error(e)
    sys.exit(1)
#
def addToSpecial(self, name, value, pathSep=None):
  "add special dangerous cases: TCLLIBPATH PV_PLUGIN_PATH etc..."
  #http://computer-programming-forum.com/57-tcl/1dfddc136afccb94.htm
  #TCLLIBPATH: Tcl treats the contents of that variable as a list. Be happy, for you can now use drive letters on windows.
  if value == '':
    return
  
  specialBlanksKeys=["TCLLIBPATH", "TKLIBPATH"]
  specialSemicolonKeys=["PV_PLUGIN_PATH"]
  res=os.pathsep
  if name in specialBlanksKeys: res=" "
  if name in specialSemicolonKeys: res=";"
  
  if pathSep==None:
    sep=res
  else:
    sep=pathSep
  value = os.path.expandvars(value) # expand environment variables
  self.getLogger().debug("Add to %s: %s", name, value)
  env = os.getenv(name, None)
  if env is None:
    os.environ[name] = value
  else:
    os.environ[name] = value + sep + env #explicitely or not special path separator ?whitespace, semicolon?

if __name__ == "__main__":
  args = sys.argv[1:]
  main(args)
#
"""
    