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

# python imports
import os
import sys
import imp
import types
import gettext

# salomeTools imports
import common.options
import config

# get path to salomeTools sources
srcdir = os.path.dirname(os.path.realpath(__file__))

# load resources for internationalization
es = gettext.translation('salomeTools', os.path.join(srcdir, 'common', 'i18n'))
es.install()

def find_command_list(dirPath):
    ''' Parse files in dirPath that end with .py : it gives commands list
    :param dirPath str: The directory path where to search the commands
    :return: cmd_list : the list containing the commands name 
    :rtype: list
    '''
    cmd_list = []
    for item in os.listdir(dirPath):
        if item.endswith('.py') and item!='salomeTools.py':
            cmd_list.append(item[:-len('.py')])
    return cmd_list

# The list of valid salomeTools commands
#lCommand = ['config', 'compile', 'prepare']
lCommand = find_command_list(srcdir)

# Define all possible option for salomeTools command :  sat <option> <args>
parser = common.options.Options()
parser.add_option('h', 'help', 'boolean', 'help', _("shows global help or help on a specific command."))
parser.add_option('o', 'overwrite', 'list', "overwrite", _("overwrites a configuration parameters."))
parser.add_option('g', 'debug', 'boolean', 'debug_mode', _("run salomeTools in debug mode."))

class salomeTools(object):
    '''The main class that stores all the commands of salomeTools
    '''
    def __init__(self, opt, dataDir=None):
        '''Initialization
        :param opt str: The sat options 
        :param: dataDir str : the directory that contain all the external data (like software pyconf and software scripts)
        '''
        # Read the salomeTools options (the list of possible options is at the beginning of this file)
        try:
            (options, argus) = parser.parse_args(opt.split(' '))
        except Exception as exc:
            write_exception(exc)
            sys.exit(-1)

        # initialization of class attributes       
        self.__dict__ = dict()
        self.cfg = None # the config that will be read using config_pyconf module
        self.options = options # the options passed to salomeTools
        self.dataDir = dataDir # default value will be <salomeTools root>/data
        # set the commands by calling the dedicated function
        self.__setCommands__(srcdir)
        
        # if the help option has been called, print help and exit
        if options.help:
            try:
                self.print_help(argus)
                sys.exit(0)
            except Exception as exc:
                write_exception(exc)
                sys.exit(1)

    def __getattr__(self, name):
        ''' overwrite of __getattr__ function in order to display a customized message in case of a wrong call
        :param name str: The name of the attribute 
        '''
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name + _(" is not a valid command"))
    
    def __setCommands__(self, dirPath):
        '''set class attributes corresponding to all commands that are in the dirPath directory
        :param dirPath str: The directory path containing the commands 
        '''
        # loop on the commands name
        for nameCmd in lCommand:
            # load the module that has name nameCmd in dirPath
            (file_, pathname, description) = imp.find_module(nameCmd, [dirPath])
            module = imp.load_module(nameCmd, file_, pathname, description)
            
            def run_command(args):
                '''The function that will load the configuration (all pyconf)
                and return the function run of the command corresponding to module
                :param args str: The directory path containing the commands 
                '''
                argv = args.split(" ")
                
                # first argument is the APPLICATION
                appliToLoad = None
                if argv != [''] and argv[0][0] != "-":
                    appliToLoad = argv[0].rstrip('*')
                    argv = argv[1:]
                
                # Read the config if it is not already done
                if not self.cfg:
                    # read the configuration from all the pyconf files    
                    cfgManager = config.ConfigManager()
                    self.cfg = cfgManager.getConfig(dataDir=self.dataDir, application=appliToLoad, options=self.options)
                
                return __module__.run(argv, self)

            # Make sure that run_command will be redefined at each iteration of the loop
            globals_up = {}
            globals_up.update(run_command.__globals__)
            globals_up.update({'__name__': nameCmd, '__module__' : module})
            func = types.FunctionType(run_command.__code__, globals_up, run_command.__name__,run_command.__defaults__, run_command.__closure__)

            # set the attribute corresponding to the command
            self.__setattr__(nameCmd, func)

    def print_help(self, opt):
        '''Prints help for a command. Function called when "sat -h <command>"
        :param argv str: the options passed (to get the command name)
        '''
        # if no command as argument (sat -h)
        if len(opt)==0:
            print_help()
            return
        # get command name
        command = opt[0]
        # read the configuration from all the pyconf files    
        cfgManager = config.ConfigManager()
        self.cfg = cfgManager.getConfig(dataDir=self.dataDir)

        # Check if this command exists
        if not hasattr(self, command):
            raise common.SatException(_("Command '%s' does not exist") % command)
        
        # Print salomeTools version
        print_version()
        
        # load the module
        module = self.get_module(command)

        # print the description of the command that is done in the command file
        if hasattr( module, "description" ) :
            print(common.printcolors.printcHeader( _("Description:") ))
            print(module.description() + '\n')

        # print the description of the command options
        if hasattr( module, "parser" ) :
            module.parser.print_help()

    def get_module(self, module):
        '''Loads a command. Function called only by print_help
        :param module str: the command to load
        '''
        # Check if this command exists
        if not hasattr(self, module):
            raise common.SatException(_("Command '%s' does not exist") % module)

        # load the module
        (file_, pathname, description) = imp.find_module(module, [srcdir])
        module = imp.load_module(module, file_, pathname, description)
        return module
 
def print_version():
    '''prints salomeTools version (in src/common/internal_config/salomeTools.pyconf)
    '''
    # read the config 
    cfgManager = config.ConfigManager()
    cfg = cfgManager.getConfig()
    # print the key corresponding to salomeTools version
    print(common.printcolors.printcHeader( _("Version: ") ) + cfg.INTERNAL.sat_version + '\n')


def print_help():
    '''prints salomeTools general help
    :param options str: the options
    '''
    print_version()
    
    print(common.printcolors.printcHeader( _("Usage: ") ) + "sat [sat_options] <command> [product] [command_options]\n")

    parser.print_help()

    # display all the available commands.
    print(common.printcolors.printcHeader(_("Available commands are:\n")))
    for command in lCommand:
        print(" - %s" % (command))
        
    # Explain how to get the help for a specific command
    print(common.printcolors.printcHeader(_("\nGetting the help for a specific command: ")) + "sat --help <command>\n")

def write_exception(exc):
    '''write exception in case of error in a command
    :param exc exception: the exception to print
    '''
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
    (options, args) = parser.parse_args(sys.argv[1:])

    # instantiate the salomeTools class with correct options
    sat = salomeTools(' '.join(sys.argv[1:]))
    # the command called
    command = args[0]
    # get dynamically the command function to call
    fun_command = sat.__getattr__(command)
    if options.debug_mode:
        # call classically the command and if it fails, show exception and stack (usual python mode)
        code = fun_command(' '.join(args[1:]))
    else:
        # catch exception in order to show less verbose but elegant message
        try:
            code = fun_command(' '.join(args[1:]))
        except Exception as exc:
            code = 1
            write_exception(exc)
    
    # exit salomeTools with the right code (0 if no errors, else 1)
    if code is None: code = 0
    sys.exit(code)
        