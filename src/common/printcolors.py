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
'''In this file is stored the mechanism that manage color prints in the terminal
'''

# define constant to use in scripts
COLOR_ERROR = 'ERROR'
COLOR_WARNING = 'WARNING'
COLOR_SUCCESS = 'SUCCESS'
COLOR_LABEL = 'LABEL'
COLOR_HEADER = 'HEADER'
COLOR_INFO = 'INFO'
COLOR_HIGLIGHT = 'HIGHLIGHT'

# the color map to use to print the colors
__colormap__ = {
    COLOR_ERROR: '\033[1m\033[31m',
    COLOR_SUCCESS: '\033[1m\033[32m',
    COLOR_WARNING: '\033[33m',
    COLOR_HEADER: '\033[34m',
    COLOR_INFO: '\033[35m',
    COLOR_LABEL: '\033[36m',
    COLOR_HIGLIGHT: '\033[97m\033[43m'
}

# list of available codes
__code_range__ = [1, 4] + list(range(30, 38)) + list(range(40, 48)) + list(range(90, 98)) + list(range(100, 108))

# print a text with colors
def printc(txt, code=''):
    # no code means 'auto mode'
    if code == '':
        striptxt = txt.strip().upper()
        if striptxt == "OK":
            code = COLOR_SUCCESS
        elif striptxt in ["KO", "NO"] or striptxt.startswith("ERR"):
            code = COLOR_ERROR
        else:
            return txt

    # no code => output the originial text
    if code not in __colormap__.keys() or __colormap__[code] == '':
        return txt

    return __colormap__[code] + txt + '\033[0m'

def printcInfo(txt):
    return printc(txt, COLOR_INFO)

def printcError(txt):
    return printc(txt, COLOR_ERROR)

def printcWarning(txt):
    return printc(txt, COLOR_WARNING)

def printcHeader(txt):
    return printc(txt, COLOR_HEADER)

def printcLabel(txt):
    return printc(txt, COLOR_LABEL)

def printcSuccess(txt):
    return printc(txt, COLOR_SUCCESS)

def printcHighlight(txt):
    return printc(txt, COLOR_HIGLIGHT)

def cleancolor(message):
    message = message.replace('\033[0m', '')
    for i in __code_range__:
        message = message.replace('\033[%dm' % i, '')
    return message

# shortcut method to print a label and a value with the info color
def print_value(logger, label, value, level=1, suffix=""):
    if logger is None:
        print("  %s = %s %s" % (label, printcInfo(str(value)), suffix))
    else:
        logger.write("  %s = %s %s\n" % (label, printcInfo(str(value)), suffix), level)

def print_color_range(start, end):
    for k in range(start, end+1):
        print("\033[%dm%3d\033[0m" % (k, k),)
    print

# This method prints the color map
def print_color_map():
    print("colormap:")
    print("{")
    for k in sorted(__colormap__.keys()):
        codes = __colormap__[k].split('\033[')
        codes = filter(lambda l: len(l) > 0, codes)
        codes = map(lambda l: l[:-1], codes)
        print(printc("  %s: '%s', " % (k, ';'.join(codes)), k))
    print("}")


