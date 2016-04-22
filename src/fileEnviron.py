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

batch_header="""@echo off

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
export prereq_install_Path=${out_dir_Path}/PREREQUISITES/INSTALL
export prereq_build_Path=${out_dir_Path}/PREREQUISITES/BUILD

###########################################################################
"""


cfgForPy_header='''# a generated SALOME Configuration file in python syntax from "sat application %s"
'''

##
# Instantiate correct FileEnvironment sub-class.
def get_file_environ(output, shell, environ=None, config=None):
    if shell == "bash":
        return BashFileEnviron(output, environ)
    if shell == "batch":
        return BatchFileEnviron(output, environ)
    if shell == "cfgForPy":
        return CfgForPyFileEnviron(output, environ, config)
    raise Exception("FileEnviron: Unknown shell = %s" % shell)

##
# Base class for shell environment.
class FileEnviron:
    def __init__(self, output, environ=None):
        self._do_init(output, environ)

    def _do_init(self, output, environ=None):
        self.output = output
        self.toclean = []
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ

    def add_line(self, number):
        self.output.write("\n" * number)

    def add_comment(self, comment):
        self.output.write("# %s\n" % comment)

    def add_echo(self, text):
        self.output.write('echo %s"\n' % text)

    def add_warning(self, warning):
        self.output.write('echo "WARNING %s"\n' % warning)

    def append_value(self, key, value, sep=os.pathsep):
        self.set(key, self.get(key) + sep + value)
        if (key, sep) not in self.toclean:
            self.toclean.append((key, sep))

    def append(self, key, value, sep=os.pathsep):
        if isinstance(value, list):
            self.append_value(key, sep.join(value), sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=os.pathsep):
        self.set(key, value + sep + self.get(key))
        if (key, sep) not in self.toclean:
            self.toclean.append((key, sep))

    def prepend(self, key, value, sep=os.pathsep):
        if isinstance(value, list):
            self.prepend_value(key, sep.join(value), sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        return self.environ.has_key(key)

    def set(self, key, value):
        raise NotImplementedError("set is not implement for this shell!")

    def get(self, key):
        return '${%s}' % key

    def command_value(self, key, command):
        raise NotImplementedError("command_value is not implement for this shell!")

    def finish(self, required=True):
        for (key, sep) in self.toclean:
            if sep != ' ':
                self.output.write('clean %s "%s"\n' % (key, sep))

##
# Class for bash shell.
class BashFileEnviron(FileEnviron):
    def __init__(self, output, environ=None):
        self._do_init(output, environ)
        self.output.write(bash_header)

    def set(self, key, value):
        self.output.write('export %s="%s"\n' % (key, value))
        self.environ[key] = value

    def command_value(self, key, command):
        self.output.write('export %s=$(%s)\n' % (key, command))

    def finish(self, required=True):
        if not required:
            return
        FileEnviron.finish(self, required)
        
##
# Class for Windows batch shell.
class BatchFileEnviron(FileEnviron):
    def __init__(self, output, environ=None):
        self._do_init(output, environ)
        self.output.write(batch_header)

    def add_comment(self, comment):
        self.output.write("rem %s\n" % comment)
    
    def get(self, key):
        return '%%%s%%' % key
    
    def set(self, key, value):
        self.output.write('set %s=%s\n' % (key, value))
        self.environ[key] = value

    def command_value(self, key, command):
        self.output.write('%s > tmp.txt\n' % (command))
        self.output.write('set /p %s =< tmp.txt\n' % (key))

    def finish(self, required=True):
        return

##
# Base class for cfg environment file.
class FileCfg:
    def __init__(self, output, environ=None):
        self._do_init(output, environ)

    def _do_init(self, output, environ=None):
        self.output = output
        self.toclean = []
        if environ is not None:
            self.environ = environ
        else:
            self.environ = os.environ
        if not self.environ.has_key("PATH"):
            self.environ["PATH"]=""
        if not self.environ.has_key("LD_LIBRARY_PATH"):
            self.environ["LD_LIBRARY_PATH"]=""
        if not self.environ.has_key("PYTHONPATH"):
            self.environ["PYTHONPATH"]=""
        if not self.environ.has_key("TCLLIBPATH"):
            self.environ["TCLLIBPATH"]=""
        if not self.environ.has_key("TKLIBPATH"):
            self.environ["TKLIBPATH"]=""


    def add_line(self, number):
        self.output.write("\n" * number)

    def add_comment(self, comment):
        self.output.write("# %s\n" % comment)

    def add_echo(self, text):
        self.output.write('# %s"\n' % text)

    def add_warning(self, warning):
        self.output.write('# "WARNING %s"\n' % warning)

    def append_value(self, key, value, sep=":"):
        if self.is_defined(key) :
            self.add(key, value)
        else :
            self.set(key, value)

    def append(self, key, value, sep=":"):
        if isinstance(value, list):
            self.append_value(key, sep.join(value), sep)
        else:
            self.append_value(key, value, sep)

    def prepend_value(self, key, value, sep=":"):
        if self.is_defined(key) :
            self.add(key, value)
        else :
            self.set(key, value)

    def prepend(self, key, value, sep=":"):
        if isinstance(value, list):
            self.prepend_value(key, sep.join(value), sep)
        else:
            self.prepend_value(key, value, sep)

    def is_defined(self, key):
        return self.environ.has_key(key)

    def set(self, key, value):
        raise NotImplementedError("set is not implement for file .cfg!")

    def get(self, key):
        return '${%s}' % key

    def command_value(self, key, command):
        raise NotImplementedError("command_value is not implement for file .cfg!")

    def finish(self, required=True):
        #for (key, sep) in self.toclean:
        #   if sep != ' ':
        #       self.output.write('clean %s "%s"\n' % (key, sep))
        #self.output.write("# finish\n")
        pass


def specialPathSeparator(name):
    """TCLLIBPATH, TKLIBPATH, PV_PLUGIN_PATH environments variables needs some exotic path separator"""
    specialBlanksKeys=["TCLLIBPATH", "TKLIBPATH"]
    specialSemicolonKeys=["PV_PLUGIN_PATH"]
    res=os.pathsep
    if name in specialBlanksKeys: res=" "
    if name in specialSemicolonKeys: res=";"
    return res

##
#
##
# Class for generate a cfg file script (in python syntax) SalomeContext API.
class CfgForPyFileEnviron(FileCfg):
    def __init__(self, output, environ=None, config=None):
        self.config=config
        self._do_init(output, environ)

        self.indent="    " # four whitespaces for first indentation in a python script
        self.prefix="context."
        self.setVarEnv="setVariable"
        
        self.begin=self.indent+self.prefix
        self.output.write((cfgForPy_header) % config['VARS']['product'])
        self.specialKeys={"PATH": "Path", "LD_LIBRARY_PATH": "LdLibraryPath", "PYTHONPATH": "PythonPath"}

    def changeToCfg(self, value):
        res=value
        return res

    def set(self, key, value):
        self.output.write(self.begin+self.setVarEnv+'(r"%s", r"%s", overwrite=True)\n' % (key, self.changeToCfg(value)))
        self.environ[key] = value

    def add(self, key, value):        
        if key in self.specialKeys.keys():
            self.output.write(self.begin+'addTo%s(r"%s")\n' % (self.specialKeys[key], self.changeToCfg(value)))
            self.environ[key]+=":"+value
            return
        sep=specialPathSeparator(key)
        self.output.write(self.indent+'#temporary solution!!! have to be defined in API a ?dangerous? addToSpecial(r"%s", r"%s")\n' % (key, value))
        #pathsep not precised because do not know future os launch?
        self.output.write(self.begin+'addToSpecial(r"%s", r"%s")\n' % (key, self.changeToCfg(value)))
        self.environ[key]+=sep+value #here yes we know os for current execution

    def command_value(self, key, command):
        #self.output.write('%s=`%s`\n' % (key, command))
        self.output.write(self.indent+'#`%s`\n' % command)

        import shlex, subprocess
        args = shlex.split(command)
        res=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, __ = res.communicate()
        self.output.write(self.begin+self.setVarEnv+'(r"%s", r"%s", overwrite=True)\n' % (key, out))       
        pass

    def add_comment(self, comment):
        if comment=="DISTENE license":
            self.output.write(self.indent+"#"+self.prefix+self.setVarEnv+'(r"%s", r"%s", overwrite=True)\n' % ('DISTENE_LICENSE_FILE', self.changeToCfg('Use global envvar: DLIM8VAR')))
            self.output.write(self.indent+"#"+self.prefix+self.setVarEnv+'(r"%s", r"%s", overwrite=True)\n' % ('DISTENE_LICENCE_FILE_FOR_MGCLEANER', self.changeToCfg('<path to your license>')))
            self.output.write(self.indent+"#"+self.prefix+self.setVarEnv+'(r"%s", r"%s", overwrite=True)\n' % ('DISTENE_LICENCE_FILE_FOR_YAMS', self.changeToCfg('<path to your license>')))
            return
        if "setting environ for" in comment:
            self.output.write(self.indent+"#[%s]\n" % comment.split("setting environ for ")[1])
            return
        if "PRODUCT environment" in comment:
            self.output.write(self.indent+"#[SALOME Configuration]\n\n")
            self.output.write(self.indent+"# PRODUCT environment\n")
            tmp=","
            for i in self.config['PRODUCT']['modules']: tmp+=i+','
            self.output.write(self.indent+"#only for information:\n")
            self.output.write(self.indent+'#'+self.setVarEnv+'("SALOME_MODULES", r"%s", overwrite=True)\n\n' % tmp[1:-1])
            try:
                #tmp1=self.config['APPLI']['module_appli']
                #tmp2=self.config.TOOLS.common.module_info[tmp1].install_dir
                tmp3=self.config.APPLI.module_appli_install_dir
                relpath=os.path.relpath("/",os.getenv("HOME"))
                tmp=relpath[0:-1]+tmp3
                self.output.write(self.indent+"#only for information: ${APPLI} is preset and have to be relative to $HOME\n")
                self.output.write(self.indent+'#'+self.setVarEnv+'("APPLI", r"%s", overwrite=True)\n\n' % tmp)
            except:
                self.output.write(self.indent+"#only for information: ${APPLI} is by default\n")
            return
        self.output.write(self.indent+"# %s\n" % comment)
        