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
__code_range__ = ([1, 4] + list(range(30, 38)) + list(range(40, 48))
                + list(range(90, 98)) + list(range(100, 108)))

def printc(txt, code=''):
    '''print a text with colors
    
    :param txt str: The text to be printed.
    :param code str: The color to use.
    :return: The colored text.
    :rtype: str
    '''
    # no code means 'auto mode' (works only for OK, KO, NO and ERR*)
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
    '''print a text info color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_INFO)

def printcError(txt):
    '''print a text error color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_ERROR)

def printcWarning(txt):
    '''print a text warning color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_WARNING)

def printcHeader(txt):
    '''print a text header color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_HEADER)

def printcLabel(txt):
    '''print a text label color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_LABEL)

def printcSuccess(txt):
    '''print a text success color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_SUCCESS)

def printcHighlight(txt):
    '''print a text highlight color
    
    :param txt str: The text to be printed.
    :return: The colored text.
    :rtype: str
    '''
    return printc(txt, COLOR_HIGLIGHT)

def cleancolor(message):
    '''remove color from a colored text.
    
    :param message str: The text to be cleaned.
    :return: The cleaned text.
    :rtype: str
    '''
    if message == None:
        return message
    
    message = message.replace('\033[0m', '')
    for i in __code_range__:
        message = message.replace('\033[%dm' % i, '')
    return message

def print_value(logger, label, value, level=1, suffix=""):
    '''shortcut method to print a label and a value with the info color
    
    :param logger class logger: the logger instance.
    :param label int: the label to print.
    :param value str: the value to print.
    :param level int: the level of verboseness.
    :param suffix str: the suffix to add at the end.
    '''
    if type(value) is list:
        skip = "\n     "
        strValue = ""
        i = 0
        for v in value:
          strValue += "%15s, " % str(v)
          i += 1
          if i >= 5:
            strValue += skip
            i = 0
        if len(value) > 5:
            strValue = skip + strValue
    else:
        strValue = str(value)
    strValue = printcInfo(strValue)
    if logger is None:
        print("  %s = %s %s" % (label, strValue, suffix))
    else:
        logger.write("  %s = %s %s\n" % (label, strValue, suffix), level)

def print_color_range(start, end):
    '''print possible range values for colors
    
    :param start int: The smaller value.
    :param end int: The bigger value.
    '''
    for k in range(start, end+1):
        print("\033[%dm%3d\033[0m" % (k, k),)
    print

# This method prints the color map
def print_color_map():
    '''This method prints the color map
    '''
    print("colormap:")
    print("{")
    for k in sorted(__colormap__.keys()):
        codes = __colormap__[k].split('\033[')
        codes = filter(lambda l: len(l) > 0, codes)
        codes = map(lambda l: l[:-1], codes)
        print(printc("  %s: '%s', " % (k, ';'.join(codes)), k))
    print("}")


