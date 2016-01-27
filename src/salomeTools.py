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

'''This file is the main entry file to salomeTools
'''

import os
import sys
import imp
import types
import gettext

import common.options
import config

# get path to salomeTools sources
srcdir = os.path.dirname(os.path.realpath(__file__))

# load resources for internationalization
#gettext.install('salomeTools', os.path.join(srcdir, 'common', 'i18n'))

es = gettext.translation('salomeTools', os.path.join(srcdir, 'common', 'i18n'))
es.install()

def find_command_list():
    cmd_list = []
    for item in os.listdir(srcdir):
        if item.endswith('.py') and item!='salomeTools.py':
            cmd_list.append(item[:-len('.py')])
    return cmd_list

# The list of valid salomeTools commands
#lCommand = ['config', 'compile', 'prepare']
lCommand = find_command_list()

# Define all possible option for salomeTools command :  sat <option> <args>
parser = common.options.Options()
parser.add_option('h', 'help', 'boolean', 'help', _(u"shows global help or help on a specific command."))

class salomeTools(object):
    def __init__(self, options, dataDir=None):
        '''Initialization
        '''
        self.__dict__ = dict()
        self.options = options
        self.dataDir = dataDir
        # set the commands
        self.__setCommands__(srcdir)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name + _(" is not a valid command"))

    def __setattr__(self, name, value):
        object.__setattr__(self,name,value)

    def __setCommands__(self, dirPath):
        for nameCmd in lCommand:
            (file_, pathname, description) = imp.find_module(nameCmd, [dirPath])
            module = imp.load_module(nameCmd, file_, pathname, description)

            def run_command(args):
                print('Je suis dans l\'initialisation de la commande ' + __name__)
                argv = args.split(" ")
                
                # first argument is the APPLICATION
                appliToLoad = None
                if len(argv) > 0 and argv[0][0] != "-":
                    appliToLoad = argv[0].rstrip('*')
                    argv = argv[1:]
                
                # read the configuration from all the pyconf files    
                cfgManager = config.ConfigManager()
                self.cfg = cfgManager.getConfig(dataDir=self.dataDir, application=appliToLoad)
                
                return __module__.run(argv, self)

            globals_up = {}
            globals_up.update(run_command.__globals__)
            globals_up.update({'__name__': nameCmd, '__module__' : module})
            func = types.FunctionType(run_command.__code__, globals_up, run_command.__name__,run_command.__defaults__, run_command.__closure__)

            self.__setattr__(nameCmd, func)
             



def print_help(options):
    #from config import ConfigManager
    #cfgManager = ConfigManager(STAND_ALONE_VERSION)
    #cfg = cfgManager.getConfig(None, options)
    #print_version(cfg)
    #print

    print(common.printcolors.printcHeader( _("Usage: ") ) + "sat [sat_options] <command> [product] [command_options]\n")

    parser.print_help()

    # parse the src directory to list the available commands.
    print(common.printcolors.printcHeader(_("Available commands are:\n")))
    for command in lCommand:
        print(" - %s" % (command))

    print(common.printcolors.printcHeader(_(u"\nGetting the help for a specific command: ")) + "sat --help <command>\n")

def write_exception(exc):
    sys.stderr.write("\n***** ")
    sys.stderr.write(common.printcolors.printcError("salomeTools ERROR:"))
    sys.stderr.write("\n" + str(exc) + "\n")

# ###############################
# MAIN : terminal command usage #
# ###############################
if __name__ == "__main__":  
    # Get the command line using sys.argv
    cmd_line = " ".join(sys.argv)
    # Initialize the code that will be returned by the terminal command 
    code = 0
    
    # Read the salomeTools options (the list of possible options is at the beginning of this file)
    try:
        (options, args) = parser.parse_args(sys.argv[1:])
    except Exception as exc:
        write_exception(exc)
        sys.exit(-1)
    
    if len(args) == 0:
        # no options => show help
        print_help(options)
    
    sat = salomeTools('')
    sat.config('-v VARS.python')
    


