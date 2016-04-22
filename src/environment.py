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

import src

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
