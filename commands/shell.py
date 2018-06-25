#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2012  CEA/DEN
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

import subprocess

import src

# Define all possible option for the shell command :  sat shell <options>
parser = src.options.Options()
parser.add_option('c', 'command', 'string', 'command',
    _('Mandatory: The shell command to execute.'), "")

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the shell command description.
    :rtype: str
    '''
    return _("""\
The shell command executes the shell commands passed as argument.

example:
>> sat shell --command "ls -l /tmp" """)
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with shell parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # Make sure the command option has been called
    if not options.command:
        message = _("The option --command is required\n")      
        logger.write(src.printcolors.printcError(message))
        return 1
    
    # Print the input command
    msg = _("Command to execute:\n%s\nExecution ... " % options.command)
    logger.write(msg, 3)
    
    # Call the input command
    res = subprocess.call(options.command,
                          shell=True,
                          stdout=logger.logTxtFile,
                          stderr=subprocess.STDOUT)
 
    # Format the result to be 0 (success) or 1 (fail)
    if res != 0:
        res = 1
        logger.write(src.printcolors.printc("KO"), 3)
    else:
        logger.write(src.printcolors.printc("OK"), 3)
    
    logger.write("\n",3)
    
    return res