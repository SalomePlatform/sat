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
import shutil
import errno
import stat

from . import pyconf
from . import architecture
from . import printcolors
from . import options
from . import system
from . import ElementTree
from . import logger
from . import product
from . import environment
from . import fileEnviron
from . import compilation
from . import test_module
from . import template

import platform
if platform.system() == "Windows" :
    import colorama
    colorama.init()

OK_STATUS = "OK"
KO_STATUS = "KO"
NA_STATUS = "NA"
KNOWNFAILURE_STATUS = "KF"
TIMEOUT_STATUS = "TIMEOUT"

CONFIG_FILENAME = "sat-config.pyconf"

class SatException(Exception):
    '''rename Exception Class
    '''
    pass

def ensure_path_exists(p):
    '''Create a path if not existing
    
    :param p str: The path.
    '''
    if not os.path.exists(p):
        os.makedirs(p)
        
def check_config_has_application( config, details = None ):
    '''check that the config has the key APPLICATION. Else raise an exception.
    
    :param config class 'common.pyconf.Config': The config.
    '''
    if 'APPLICATION' not in config:
        message = _("An APPLICATION is required. Use 'config --list' to get"
                    " the list of available applications.\n")
        if details :
            details.append(message)
        raise SatException( message )

def check_config_has_profile( config, details = None ):
    '''check that the config has the key APPLICATION.profile.
       Else, raise an exception.
    
    :param config class 'common.pyconf.Config': The config.
    '''
    check_config_has_application(config)
    if 'profile' not in config.APPLICATION:
        message = _("A profile section is required in your application.\n")
        if details :
            details.append(message)
        raise SatException( message )

def config_has_application( config ):
    return 'APPLICATION' in config

def get_cfg_param(config, param_name, default):
    '''Search for param_name value in config.
       If param_name is not in config, then return default,
       else, return the found value
       
    :param config class 'common.pyconf.Config': The config.
    :param param_name str: the name of the parameter to get the value
    :param default str: The value to return if param_name is not in config
    :return: see initial description of the function
    :rtype: str
    '''
    if param_name in config:
        return config[param_name]
    return default

def print_info(logger, info):
    '''Prints the tuples that are in info variable in a formatted way.
    
    :param logger Logger: The logging instance to use for the prints.
    :param info list: The list of tuples to display
    '''
    # find the maximum length of the first value of the tuples in info
    smax = max(map(lambda l: len(l[0]), info))
    # Print each item of info with good indentation
    for i in info:
        sp = " " * (smax - len(i[0]))
        printcolors.print_value(logger, sp + i[0], i[1], 2)
    logger.write("\n", 2)

def get_base_path(config):
    '''Returns the path of the products base.
    
    :param config Config: The global Config instance.
    :return: The path of the products base.
    :rtype: str
    '''
    if "base" not in config.LOCAL:
        local_file_path = os.path.join(config.VARS.salometoolsway,
                                      "data",
                                      "local.pyconf")
        msg = _("Please define a base path in the file %s" % local_file_path)
        raise SatException(msg)
        
    base_path = os.path.abspath(config.LOCAL.base)
    
    return base_path

def get_launcher_name(config):
    '''Returns the name of salome launcher.
    
    :param config Config: The global Config instance.
    :return: The name of salome launcher.
    :rtype: str
    '''
    check_config_has_application(config)
    if 'profile' in config.APPLICATION and 'launcher_name' in config.APPLICATION.profile:
        launcher_name = config.APPLICATION.profile.launcher_name
    else:
        launcher_name = 'salome'

    return launcher_name

def get_log_path(config):
    '''Returns the path of the logs.
    
    :param config Config: The global Config instance.
    :return: The path of the logs.
    :rtype: str
    '''
    if "log_dir" not in config.LOCAL:
        local_file_path = os.path.join(config.VARS.salometoolsway,
                                      "data",
                                      "local.pyconf")
        msg = _("Please define a log_dir in the file %s" % local_file_path)
        raise SatException(msg)
      
    log_dir_path = os.path.abspath(config.LOCAL.log_dir)
    
    return log_dir_path

def get_salome_version(config):
    if hasattr(config.APPLICATION, 'version_salome'):
        Version = config.APPLICATION.version_salome
    else:
        KERNEL_info = product.get_product_config(config, "KERNEL")
        VERSION = os.path.join(
                            KERNEL_info.install_dir,
                            "bin",
                            "salome",
                            "VERSION")
        if not os.path.isfile(VERSION):
            return None
            
        fVERSION = open(VERSION)
        Version = fVERSION.readline()
        fVERSION.close()
        
    VersionSalome = int(only_numbers(Version))    
    return VersionSalome

def only_numbers(str_num):
    return ''.join([nb for nb in str_num if nb in '0123456789'] or '0')

def read_config_from_a_file(filePath):
        try:
            cfg_file = pyconf.Config(filePath)
        except pyconf.ConfigError as e:
            raise SatException(_("Error in configuration file: %(file)s\n  %(error)s") % \
                { 'file': filePath, 'error': str(e) })
        return cfg_file

def get_tmp_filename(cfg, name):
    if not os.path.exists(cfg.VARS.tmp_root):
        os.makedirs(cfg.VARS.tmp_root)

    return os.path.join(cfg.VARS.tmp_root, name)

##
# Utils class to simplify path manipulations.
class Path:
    def __init__(self, path):
        self.path = str(path)

    def __add__(self, other):
        return Path(os.path.join(self.path, str(other)))

    def __abs__(self):
        return Path(os.path.abspath(self.path))

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    def exists(self):
        return self.islink() or os.path.exists(self.path)

    def islink(self):
        return os.path.islink(self.path)

    def isdir(self):
        return os.path.isdir(self.path)

    def isfile(self):
        return os.path.isfile(self.path)

    def list(self):
        return [Path(p) for p in os.listdir(self.path)]

    def dir(self):
        return Path(os.path.dirname(self.path))

    def base(self):
        return Path(os.path.basename(self.path))

    def make(self, mode=None):
        os.makedirs(self.path)        
        if mode:
            os.chmod(self.path, mode)
        
    def chmod(self, mode):
        os.chmod(self.path, mode)

    def rm(self):    
        if self.islink():
            os.remove(self.path)
        else:
            shutil.rmtree( self.path, onerror = handleRemoveReadonly )

    def copy(self, path, smart=False):
        if not isinstance(path, Path):
            path = Path(path)

        if os.path.islink(self.path):
            return self.copylink(path)
        elif os.path.isdir(self.path):
            return self.copydir(path, smart)
        else:
            return self.copyfile(path)

    def smartcopy(self, path):
        return self.copy(path, True)

    def readlink(self):
        if self.islink():
            return os.readlink(self.path)
        else:
            return False

    def symlink(self, path):
        try:
            os.symlink(str(path), self.path)
            return True
        except:
            return False

    def copylink(self, path):
        try:
            os.symlink(os.readlink(self.path), str(path))
            return True
        except:
            return False

    def copydir(self, dst, smart=False):
        try:
            names = self.list()

            if not dst.exists():
                dst.make()

            for name in names:
                if name == dst:
                    continue
                if smart and (str(name) in [".git", "CVS", ".svn"]):
                    continue
                srcname = self + name
                dstname = dst + name
                srcname.copy(dstname, smart)
            return True
        except:
            return False

    def copyfile(self, path):
        try:
            shutil.copy2(self.path, str(path))
            return True
        except:
            return False

def find_file_in_lpath(file_name, lpath, additional_dir = ""):
    """Find in all the directories in lpath list the file that has the same name
       as file_name. If it is found, return the full path of the file, else,
       return False. 
       The additional_dir (optional) is the name of the directory to add to all 
       paths in lpath.
    
    :param file_name str: The file name to search
    :param lpath List: The list of directories where to search
    :param additional_dir str: The name of the additional directory
    :return: the full path of the file or False if not found
    :rtype: str
    """
    for directory in lpath:
        dir_complete = os.path.join(directory, additional_dir)
        if not os.path.isdir(directory) or not os.path.isdir(dir_complete):
            continue
        l_files = os.listdir(dir_complete)
        for file_n in l_files:
            if file_n == file_name:
                return os.path.join(dir_complete, file_name)
    return False

def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise

def deepcopy_list(input_list):
    """ Do a deep copy of a list
    
    :param input_list List: The list to copy
    :return: The copy of the list
    :rtype: List
    """
    res = []
    for elem in input_list:
        res.append(elem)
    return res

def remove_item_from_list(input_list, item):
    """ Remove all occurences of item from input_list
    
    :param input_list List: The list to modify
    :return: The without any item
    :rtype: List
    """
    res = []
    for elem in input_list:
        if elem == item:
            continue
        res.append(elem)
    return res

def parse_date(date):
    """Transform YYYYMMDD_hhmmss into YYYY-MM-DD hh:mm:ss.
    
    :param date str: The date to transform
    :return: The date in the new format
    :rtype: str
    """
    if len(date) != 15:
        return date
    res = "%s-%s-%s %s:%s:%s" % (date[0:4],
                                 date[4:6],
                                 date[6:8],
                                 date[9:11],
                                 date[11:13],
                                 date[13:])
    return res

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def replace_in_file(filein, strin, strout):
    '''Replace <strin> by <strout> in file <filein>
    '''
    shutil.move(filein, filein + "_old")
    fileout= filein
    filein = filein + "_old"
    fin = open(filein, "r")
    fout = open(fileout, "w")
    for line in fin:
        fout.write(line.replace(strin, strout))

def get_property_in_product_cfg(product_cfg, pprty):
    if not "properties" in product_cfg:
        return None
    if not pprty in product_cfg.properties:
        return None
    return product_cfg.properties[pprty]
