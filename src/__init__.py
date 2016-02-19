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

from . import pyconf
from . import architecture
from . import printcolors
from . import options
from . import system
from . import ElementTree
from . import logger

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

def config_has_application( config ):
    return 'APPLICATION' in config
    
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