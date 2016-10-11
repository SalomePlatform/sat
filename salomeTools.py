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
import tempfile
import imp
import types
import gettext

# salomeTools imports
import src

# get path to salomeTools sources
satdir  = os.path.dirname(os.path.realpath(__file__))
cmdsdir = os.path.join(satdir, 'commands')

# Make the src package accessible from all code
sys.path.append(satdir)
sys.path.append(cmdsdir)

import config

# load resources for internationalization
#es = gettext.translation('salomeTools', os.path.join(satdir, 'src', 'i18n'))
#es.install()
gettext.install('salomeTools', os.path.join(satdir, 'src', 'i18n'))

# The possible hooks : 
# pre is for hooks to be executed before commands
# post is for hooks to be executed after commands
C_PRE_HOOK = "pre"
C_POST_HOOK = "post"

def find_command_list(dirPath):
    ''' Parse files in dirPath that end with .py : it gives commands list
    
    :param dirPath str: The directory path where to search the commands
    :return: cmd_list : the list containing the commands name 
    :rtype: list
    '''
    cmd_list = []
    for item in os.listdir(dirPath):
        if item.endswith('.py'):
            cmd_list.append(item[:-len('.py')])
    return cmd_list

# The list of valid salomeTools commands
#lCommand = ['config', 'compile', 'prepare']
lCommand = find_command_list(cmdsdir)

# Define all possible option for salomeTools command :  sat <option> <args>
parser = src.options.Options()
parser.add_option('h', 'help', 'boolean', 'help', 
                  _("shows global help or help on a specific command."))
parser.add_option('o', 'overwrite', 'list', "overwrite", 
                  _("overwrites a configuration parameters."))
parser.add_option('g', 'debug', 'boolean', 'debug_mode', 
                  _("run salomeTools in debug mode."))
parser.add_option('v', 'verbose', 'int', "output_verbose_level", 
                  _("change output verbose level (default is 3)."))
parser.add_option('b', 'batch', 'boolean', "batch", 
                  _("batch mode (no question)."))
parser.add_option('t', 'all_in_terminal', 'boolean', "all_in_terminal", 
                  _("All traces in the terminal (for example compilation logs)."))
parser.add_option('l', 'logs_paths_in_file', 'string', "logs_paths_in_file", 
                  _("Put the command result and paths to log files in ."))

class Sat(object):
    '''The main class that stores all the commands of salomeTools
    '''
    def __init__(self, opt='', datadir=None):
        '''Initialization
        
        :param opt str: The sat options 
        :param: datadir str : the directory that contain all the external 
                              data (like software pyconf and software scripts)
        '''
        # Read the salomeTools options (the list of possible options is 
        # at the beginning of this file)
        try:
            (options, argus) = parser.parse_args(opt.split(' '))
        except Exception as exc:
            write_exception(exc)
            sys.exit(-1)

        # initialization of class attributes       
        self.__dict__ = dict()
        self.cfg = None # the config that will be read using pyconf module
        self.arguments = opt
        self.options = options # the options passed to salomeTools
        self.datadir = datadir # default value will be <salomeTools root>/data
        # set the commands by calling the dedicated function
        self._setCommands(cmdsdir)
        
        # if the help option has been called, print help and exit
        if options.help:
            try:
                self.print_help(argus)
                sys.exit(0)
            except Exception as exc:
                write_exception(exc)
                sys.exit(1)

    def __getattr__(self, name):
        ''' overwrite of __getattr__ function in order to display 
            a customized message in case of a wrong call
        
        :param name str: The name of the attribute 
        '''
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name + _(" is not a valid command"))
    
    def _setCommands(self, dirPath):
        '''set class attributes corresponding to all commands that are 
           in the dirPath directory
        
        :param dirPath str: The directory path containing the commands 
        '''
        # loop on the commands name
        for nameCmd in lCommand:
            
            # Exception for the jobs command that requires the paramiko module
            if nameCmd == "jobs":
                try:
                    saveout = sys.stderr
                    ff = tempfile.TemporaryFile()
                    sys.stderr = ff
                    import paramiko
                    sys.stderr = saveout
                except:
                    sys.stderr = saveout
                    continue

            # load the module that has name nameCmd in dirPath
            (file_, pathname, description) = imp.find_module(nameCmd, [dirPath])
            module = imp.load_module(nameCmd, file_, pathname, description)
            
            def run_command(args='',
                            batch = False,
                            verbose = -1,
                            logger_add_link = None):
                '''The function that will load the configuration (all pyconf)
                and return the function run of the command corresponding to module
                
                :param args str: The directory path containing the commands 
                '''
                # Make sure the internationalization is available
                gettext.install('salomeTools',
                                os.path.join(satdir, 'src', 'i18n'))
                
                # Get the arguments in a list and remove the empty elements
                argv_0 = args.split(" ")
                if argv_0 != ['']:
                    while "" in argv_0: argv_0.remove("")
                
                # Format the argv list in order to prevent strings 
                # that contain a blank to be separated
                argv = []
                elem_old = ""
                for elem in argv_0:
                    if argv == [] or elem_old.startswith("-") or elem.startswith("-"):
                        argv.append(elem)
                    else:
                        argv[-1] += " " + elem
                    elem_old = elem
                           
                # if it is provided by the command line, get the application
                appliToLoad = None
                if argv != [''] and argv[0][0] != "-":
                    appliToLoad = argv[0].rstrip('*')
                    argv = argv[1:]
   
                # read the configuration from all the pyconf files    
                cfgManager = config.ConfigManager()
                self.cfg = cfgManager.get_config(datadir=self.datadir, 
                                                 application=appliToLoad, 
                                                 options=self.options, 
                                                 command=__nameCmd__)
                
                # Set the verbose mode if called
                if verbose > -1:
                    verbose_save = self.options.output_verbose_level
                    self.options.__setattr__("output_verbose_level", verbose)    

                # Set batch mode if called
                if batch:
                    batch_save = self.options.batch
                    self.options.__setattr__("batch", True)

                # set output level
                if self.options.output_verbose_level is not None:
                    self.cfg.USER.output_verbose_level = self.options.output_verbose_level
                if self.cfg.USER.output_verbose_level < 1:
                    self.cfg.USER.output_verbose_level = 0
                silent = (self.cfg.USER.output_verbose_level == 0)

                # create log file
                micro_command = False
                if logger_add_link:
                    micro_command = True
                logger_command = src.logger.Logger(self.cfg, 
                                   silent_sysstd=silent,
                                   all_in_terminal=self.options.all_in_terminal,
                                   micro_command=micro_command)
                
                # Check that the path given by the logs_paths_in_file option
                # is a file path that can be written
                if self.options.logs_paths_in_file:
                    try:
                        self.options.logs_paths_in_file = os.path.abspath(
                                                self.options.logs_paths_in_file)
                        dir_file = os.path.dirname(self.options.logs_paths_in_file)
                        if not os.path.exists(dir_file):
                            os.makedirs(dir_file)
                        if os.path.exists(self.options.logs_paths_in_file):
                            os.remove(self.options.logs_paths_in_file)
                        file_test = open(self.options.logs_paths_in_file, "w")
                        file_test.close()
                    except Exception as e:
                        msg = _("WARNING: the logs_paths_in_file option will "
                                "not be taken into account.\nHere is the error:")
                        logger_command.write("%s\n%s\n\n" % (
                                             src.printcolors.printcWarning(msg),
                                             str(e)))
                        self.options.logs_paths_in_file = None
                
                try:
                    res = None
                    # Execute the hooks (if there is any) 
                    # and run method of the command
                    self.run_hook(__nameCmd__, C_PRE_HOOK, logger_command)
                    res = __module__.run(argv, self, logger_command)
                    self.run_hook(__nameCmd__, C_POST_HOOK, logger_command)
                    
                    # set res if it is not set in the command
                    if res is None:
                        res = 0
                    
                    # come back in the original batch mode if 
                    # batch argument was called
                    if batch:
                        self.options.__setattr__("batch", batch_save)

                    # come back in the original verbose mode if 
                    # verbose argument was called                        
                    if verbose > -1:
                        self.options.__setattr__("output_verbose_level", 
                                                 verbose_save)
                    # put final attributes in xml log file 
                    # (end time, total time, ...) and write it
                    launchedCommand = ' '.join([self.cfg.VARS.salometoolsway +
                                                os.path.sep +
                                                'sat',
                                                __nameCmd__, 
                                                args])
                    launchedCommand = launchedCommand.replace('"', "'")
                    
                    # Add a link to the parent command      
                    if logger_add_link is not None:
                        logger_add_link.add_link(logger_command.logFileName,
                                                 __nameCmd__,
                                                 res,
                                                 launchedCommand)
                        logger_add_link.l_logFiles += logger_command.l_logFiles

                finally:
                    launchedCommand = ' '.join([self.cfg.VARS.salometoolsway +
                                                os.path.sep +
                                                'sat',
                                                __nameCmd__, 
                                                args])
                    launchedCommand = launchedCommand.replace('"', "'")
                    
                    # Put the final attributes corresponding to end time and
                    # Write the file to the hard drive
                    logger_command.end_write(
                                        {"launchedCommand" : launchedCommand})
                    
                    if res != 0:
                        res = 1
                    # If the logs_paths_in_file was called, write the result
                    # and log files in the given file path
                    if self.options.logs_paths_in_file:
                        file_res = open(self.options.logs_paths_in_file, "w")
                        file_res.write(str(res) + "\n")
                        for i, filepath in enumerate(logger_command.l_logFiles):
                            file_res.write(filepath)
                            if i < len(logger_command.l_logFiles):
                                file_res.write("\n")
                
                return res

            # Make sure that run_command will be redefined 
            # at each iteration of the loop
            globals_up = {}
            globals_up.update(run_command.__globals__)
            globals_up.update({'__nameCmd__': nameCmd, '__module__' : module})
            func = types.FunctionType(run_command.__code__,
                                      globals_up,
                                      run_command.__name__,
                                      run_command.__defaults__,
                                      run_command.__closure__)

            # set the attribute corresponding to the command
            self.__setattr__(nameCmd, func)

    def run_hook(self, cmd_name, hook_type, logger):
        '''Execute a hook file for a given command regarding the fact 
           it is pre or post
        
        :param cmd_name str: The the command on which execute the hook
        :param hook_type str: pre or post
        :param logger Logger: the logging instance to use for the prints
        '''
        # The hooks must be defined in the application pyconf
        # So, if there is no application, do not do anything
        if not src.config_has_application(self.cfg):
            return

        # The hooks must be defined in the application pyconf in the
        # APPLICATION section, hook : { command : 'script_path.py'}
        if "hook" not in self.cfg.APPLICATION \
                    or cmd_name not in self.cfg.APPLICATION.hook:
            return

        # Get the hook_script path and verify that it exists
        hook_script_path = self.cfg.APPLICATION.hook[cmd_name]
        if not os.path.exists(hook_script_path):
            raise src.SatException(_("Hook script not found: %s") % 
                                   hook_script_path)
        
        # Try to execute the script, catch the exception if it fails
        try:
            # import the module (in the sense of python)
            pymodule = imp.load_source(cmd_name, hook_script_path)
            
            # format a message to be printed at hook execution
            msg = src.printcolors.printcWarning(_("Run hook script"))
            msg = "%s: %s\n" % (msg, 
                                src.printcolors.printcInfo(hook_script_path))
            
            # run the function run_pre_hook if this function is called 
            # before the command, run_post_hook if it is called after
            if hook_type == C_PRE_HOOK and "run_pre_hook" in dir(pymodule):
                logger.write(msg, 1)
                pymodule.run_pre_hook(self.cfg, logger)
            elif hook_type == C_POST_HOOK and "run_post_hook" in dir(pymodule):
                logger.write(msg, 1)
                pymodule.run_post_hook(self.cfg, logger)

        except Exception as exc:
            msg = _("Unable to run hook script: %s") % hook_script_path
            msg += "\n" + str(exc)
            raise src.SatException(msg)

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
        self.cfg = cfgManager.get_config(datadir=self.datadir)

        # Check if this command exists
        if not hasattr(self, command):
            raise src.SatException(_("Command '%s' does not exist") % command)
        
        # Print salomeTools version
        print_version()
        
        # load the module
        module = self.get_module(command)

        # print the description of the command that is done in the command file
        if hasattr( module, "description" ) :
            print(src.printcolors.printcHeader( _("Description:") ))
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
            raise src.SatException(_("Command '%s' does not exist") % module)

        # load the module
        (file_, pathname, description) = imp.find_module(module, [cmdsdir])
        module = imp.load_module(module, file_, pathname, description)
        return module
 
def print_version():
    '''prints salomeTools version (in src/internal_config/salomeTools.pyconf)
    '''
    # read the config 
    cfgManager = config.ConfigManager()
    cfg = cfgManager.get_config()
    # print the key corresponding to salomeTools version
    print(src.printcolors.printcHeader( _("Version: ") ) + 
          cfg.INTERNAL.sat_version + '\n')


def print_help():
    '''prints salomeTools general help
    
    :param options str: the options
    '''
    print_version()
    
    print(src.printcolors.printcHeader( _("Usage: ") ) + 
          "sat [sat_options] <command> [product] [command_options]\n")

    parser.print_help()

    # display all the available commands.
    print(src.printcolors.printcHeader(_("Available commands are:\n")))
    for command in lCommand:
        print(" - %s" % (command))
        
    # Explain how to get the help for a specific command
    print(src.printcolors.printcHeader(_("\nGetting the help for a specific"
                                    " command: ")) + "sat --help <command>\n")

def write_exception(exc):
    '''write exception in case of error in a command
    
    :param exc exception: the exception to print
    '''
    sys.stderr.write("\n***** ")
    sys.stderr.write(src.printcolors.printcError("salomeTools ERROR:"))
    sys.stderr.write("\n" + str(exc) + "\n")

# ###############################
# MAIN : terminal command usage #
# ###############################
if __name__ == "__main__":  
    # Initialize the code that will be returned by the terminal command 
    code = 0
    (options, args) = parser.parse_args(sys.argv[1:])
    
    # no arguments : print general help
    if len(args) == 0:
        print_help()
        sys.exit(0)
    
    # instantiate the salomeTools class with correct options
    sat = Sat(' '.join(sys.argv[1:]))
    # the command called
    command = args[0]
    # get dynamically the command function to call
    fun_command = sat.__getattr__(command)
    # call the command with two cases : mode debug or not
    if options.debug_mode:
        # call classically the command and if it fails, 
        # show exception and stack (usual python mode)
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
        