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

"""
This file is the main API file for salomeTools

| Warning: NO '__main__ ' call allowed,
|          Use 'sat' (in parent directory)
|
| Usage: see file ../sat
"""

import sys

# exit OKSYS and KOSYS seems equal on linux or windows
_OKSYS = 0  # OK
_KOSYS = 1  # KO

########################################################################
# NO __main__ entry allowed, use sat
########################################################################
if __name__ == "__main__":
    msg = """
ERROR: 'salomeTools.py' is not main command entry (CLI) for salomeTools.
       Use 'sat' instead.\n\n"""
    sys.stderr.write(msg)
    sys.exit(_KOSYS)

# python imports
import os
import re
import tempfile
import imp
import types
import gettext
import traceback

import src
import src.debug as DBG # Easy print stderr (for DEBUG only)
import src.returnCode as RCO # Easy (ok/ko, why) return methods code
import src.utilsSat as UTS

# get path to salomeTools sources
satdir  = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
srcdir = os.path.join(satdir, 'src')
cmdsdir = os.path.join(satdir, 'commands')

import commands.config as CONFIG

# load resources for internationalization
gettext.install("salomeTools", os.path.join(srcdir, "i18n"))

try:
  _LANG = os.environ["LANG"] # original locale
except:
  _LANG = "en_US.utf8" #default

# The possible hooks : 
# pre is for hooks to be executed before commands
# post is for hooks to be executed after commands
C_PRE_HOOK = "pre"
C_POST_HOOK = "post"

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
                  _("all traces in the terminal (for example compilation logs)."))
parser.add_option('l', 'logs_paths_in_file', 'string', "logs_paths_in_file", 
                  _("put the command results and paths to log files."))


########################################################################
# utility methods
########################################################################
def find_command_list(dirPath):
    ''' Parse files in dirPath that end with .py : it gives commands list
    
    :param dirPath str: The directory path where to search the commands
    :return: cmd_list : the list containing the commands name 
    :rtype: list
    '''
    cmd_list = []
    for item in os.listdir(dirPath):
        if "__init__" in item: continue # skip __init__.py
        if item.endswith('.py'):
            cmd_list.append(item[:-len('.py')])
    return cmd_list


# The list of valid salomeTools commands from cmdsdir
# ['config', 'compile', 'prepare', ...]
_COMMANDS_NAMES = find_command_list(cmdsdir)
lCommand = find_command_list(cmdsdir) # obsolete

def getCommandsList():
    """Gives commands list (as basename of files .py in directory commands""" 
    return _COMMANDS_NAMES

def launchSat(command, logger=None):
    """
    launch sat as subprocess.Popen
    command as string ('sat --help' for example)
    used for unittest, or else...
    
    :return: RCO.ReturnCode with getValue as subprocess.Popen output
    """
    if "sat" not in command.split()[0]:
      raise Exception(_("Not a valid command for launchSat: '%s'") % command)
    env = dict(os.environ) # copy
    # theorically useless, in user environ $PATH,
    # on ne sait jamais
    # https://docs.python.org/2/library/os.html
    # On some platforms, including FreeBSD and Mac OS X, 
    # setting environ may cause memory leaks.
    # see test/initializeTest.py
    if satdir not in env["PATH"].split(":"):
      env["PATH"] = satdir + ":" + env["PATH"]
    # TODO setLocale not 'fr' on subprocesses, why not?
    # env["LANG"] == ''
    res = UTS.Popen(command, env=env, logger=logger) # logger or not.
    return res

def setNotLocale():
    """force english at any moment"""
    os.environ["LANG"] = ''
    gettext.install("salomeTools", os.path.join(srcdir, "i18n"))
    DBG.write("setNotLocale", os.environ["LANG"])
    
def setLocale():
    """
    reset initial locale at any moment 
    'fr' or else (TODO) from initial environment var '$LANG'
    'i18n' as 'internationalization'
    """
    os.environ["LANG"] = _LANG
    gettext.install("salomeTools", os.path.join(srcdir, "i18n"))
    DBG.write("setLocale", os.environ["LANG"])
    
def getVersion():
    """get version number as string"""
    return src.__version__
 
def assumeAsList(strOrList):
    """return a list as sys.argv if string"""
    if type(strOrList) is list:
      return list(strOrList) # copy
    else:
      res = strOrList.split(" ")
      return [r for r in res if r != ""] # supposed string to split for convenience


########################################################################
# Sat class
########################################################################
class Sat(object):
    """
    The main class that stores all the commands of salomeTools
    """
    def __init__(self, logger=None):
        """
        Initialization

        :param logger: The logger, if set from parent
        """
        # initialization of class attributes
        self.__dict__ = dict()
        # logger from parent
        # future only one logger from src.loggingSimple at 2018/06
        # to replace old loggers from src.logger
        self.mainLogger = logger
        src.logger.setCurrentLogger(logger)
        self.cfg = None  # the config that will be read using pyconf module
        self.arguments = None
        self.remaindersArgs = None
        self.options = None  # the options passed to salomeTools
        self.datadir = None  # default value will be <salomeTools root>/data

    def obsolete__init__(self, opt='', datadir=None):
        '''Initialization

        :param opt str: The sat options
        :param: datadir str : the directory that contain all the external
                              data (like software pyconf and software scripts)
        '''
        # Read the salomeTools options (the list of possible options is
        # at the beginning of this file)
        argList = self.assumeAsList(opt)
        options, argus = parser.parse_args(argList)

        # initialization of class attributes
        self.__dict__ = dict()
        self.cfg = None  # the config that will be read using pyconf module
        self.arguments = argList
        self.options = options  # the options passed to salomeTools
        self.datadir = datadir  # default value will be <salomeTools root>/data
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

    ##################################################################
    def setInternals(self, opt=None, datadir=None):
        """set the commands by calling the dedicated function etc..."""
        options, remaindersArgs = parser.parse_args(opt)
        if options.debug_mode:
            DBG.push_debug(True)
        self.arguments = opt
        self.options = options # the generic options passed to salomeTools
        self.remaindersArgs = remaindersArgs  # the command and their options
        self.datadir = datadir # default value will be <salomeTools root>/data
        self._setCommands(cmdsdir)
        DBG.write("Sat.options", self.options, self.options.debug_mode)

    def getConfig(self):
        return self.cfg

    ##################################################################
    def execute_cli(self, args):
        """
        assume launch command from args, pyconf config known yet
        """
        argList = self.assumeAsList(args)
        # no arguments : print general help
        if len(argList) == 0:
          self.mainLogger.info(get_help())
          return RCO.ReturnCode("OK", "no args as sat --help")

        self.setInternals(opt=argList, datadir=None)

        # print general help on -h
        if self.options.help and len(self.remaindersArgs) == 0:
          self.mainLogger.info(get_help())
          return RCO.ReturnCode("OK", "help done")

        DBG.write("options", self.options)
        DBG.write("remaindersArgs", self.remaindersArgs)

        if len(self.remaindersArgs) == 0:
          return RCO.ReturnCode("KO", "Nothing to do")

        # print command help on -h --help after name command
        if "-h" in self.remaindersArgs or "--help" in self.remaindersArgs:
          self.mainLogger.info(self.get_help(self.remaindersArgs))
          return RCO.ReturnCode("OK", "sat --help command")

        # print command help on -h and continue if something do do more
        if self.options.help and len(self.remaindersArgs) >= 1:
          self.mainLogger.info(self.get_help(self.remaindersArgs))

        command = self.remaindersArgs[0]
        # get dynamically the command function to call
        fun_command = self.__getattr__(command)
        # Run the command using the arguments
        code = fun_command(self.remaindersArgs[1:])

        if code is None: code = 0 # what?! do not know why so respect history

        # return salomeTools command with the right message
        # code (0 if no errors, else 1)
        if code == _KOSYS:
          return RCO.ReturnCode("KO", "problem on execute_cli 'sat %s'" % " ".join(argList))
        else:
          return RCO.ReturnCode("OK", "execute_cli 'sat %s' done" % " ".join(argList))

    '''
    # OBSOLETE... see file ../sat
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
        sat = Sat(sys.argv[1:])
        # the command called
        command = args[0]
        # get dynamically the command function to call
        fun_command = sat.__getattr__(command)
        # Run the command using the arguments
        code = fun_command(args[1:])

        # exit salomeTools with the right code (0 if no errors, else 1)
        if code is None: code = 0
        sys.exit(code)

    '''

    def __getattr__(self, name):
        '''
        overwrite of __getattr__ function in order to display
        a customized message in case of a wrong call
        
        :param name str: The name of the attribute 
        '''
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name + _(" is not a valid command"))

    def assumeAsList(self, strOrList):
        # DBG.write("Sat assumeAsList", strOrList, True)
        return assumeAsList(strOrList)
    
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
                            options=None,
                            batch = False,
                            verbose = -1,
                            logger_add_link = None):
                '''
                The function that will load the configuration (all pyconf)
                and return the function run of the command corresponding to module
                
                :param args str: The arguments of the command 
                '''
                # Make sure the internationalization is available
                gettext.install('salomeTools', os.path.join(satdir, 'src', 'i18n'))
                
                # Get the arguments in a list and remove the empty elements
                if type(args) == type(''):
                    # split by spaces without considering spaces in quotes
                    argv_0 = re.findall(r'(?:"[^"]*"|[^\s"])+', args)
                else:
                    argv_0 = args
                
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
                if argv not in [[''], []] and argv[0][0] != "-":
                    appliToLoad = argv[0].rstrip('*')
                    argv = argv[1:]
                
                # Check if the global options of salomeTools have to be changed
                if options:
                    options_save = self.options
                    self.options = options  

                # read the configuration from all the pyconf files    
                cfgManager = CONFIG.ConfigManager()
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
                if self.options.logs_paths_in_file and not micro_command:
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


                # do nothing more if help is True
                if self.options.help:
                  return 0

                options_launched = ""
                res = None
                try:
                    # Execute the hooks (if there is any) 
                    # and run method of the command
                    self.run_hook(__nameCmd__, C_PRE_HOOK, logger_command)
                    res = __module__.run(argv, self, logger_command)
                    self.run_hook(__nameCmd__, C_POST_HOOK, logger_command)
                    if res is None:
                        res = 0
                        
                except src.SatException as e:
                    # for sat exception do not display the stack, unless debug mode is set
                    logger_command.write("\n***** ", 1)
                    logger_command.write(src.printcolors.printcError(
                            "salomeTools ERROR: sat %s" % __nameCmd__), 1)
                    logger_command.write(" *****\n", 1)
                    print(e.message)
                    if self.options.debug_mode:
                        logger_command.write("\n" + DBG.format_exception("") + "\n", 1)

                except Exception as e:
                    # here we print the stack in addition
                    logger_command.write("\n***** ", 1)
                    logger_command.write(src.printcolors.printcError(
                            "salomeTools ERROR: sat %s" % __nameCmd__), 1)

                    logger_command.write("\n" + DBG.format_exception("") + "\n", 1)


                finally:
                    # set res if it is not set in the command
                    if res is None:
                        res = 1
                                            
                    # come back to the original global options
                    if options:
                        options_launched = get_text_from_options(self.options)
                        self.options = options_save
                    
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
                                                options_launched,
                                                __nameCmd__, 
                                                ' '.join(argv_0)])
                    # TODO may be no need as call escapeSequence xml
                    launchedCommand = launchedCommand.replace('"', "'")
                    
                    # Add a link to the parent command      
                    if logger_add_link is not None:
                        logger_add_link.add_link(logger_command.logFileName,
                                                 __nameCmd__,
                                                 res,
                                                 launchedCommand)
                        logger_add_link.l_logFiles += logger_command.l_logFiles
                                            
                    # Put the final attributes corresponding to end time and
                    # Write the file to the hard drive
                    logger_command.end_write(
                                        {"launchedCommand" : launchedCommand})
                    
                    if res != 0:
                        res = 1
                        
                    # print the log file path if 
                    # the maximum verbose mode is invoked
                    if not micro_command:
                        logger_command.write("\nPath to the xml log file :\n",
                                             5)
                        logger_command.write("%s\n\n" % src.printcolors.printcInfo(
                                                logger_command.logFilePath), 5)

                    # If the logs_paths_in_file was called, write the result
                    # and log files in the given file path
                    if self.options.logs_paths_in_file and not micro_command:
                        file_res = open(self.options.logs_paths_in_file, "w")
                        file_res.write(str(res) + "\n")
                        for i, filepath in enumerate(logger_command.l_logFiles):
                            file_res.write(filepath)
                            if i < len(logger_command.l_logFiles):
                                file_res.write("\n")
                                file_res.flush()
                
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

    def get_help(self, opt):
        '''Prints help for a command. Function called when "sat -h <command>"
        
        :param argv str: the options passed (to get the command name)
        '''
        # if no command as argument (sat -h)
        if len(opt)==0:
            return get_help()
        # get command name
        command = opt[0]
        # read the configuration from all the pyconf files
        cfgManager = CONFIG.ConfigManager()
        self.cfg = cfgManager.get_config(datadir=self.datadir)

        # Check if this command exists
        if not hasattr(self, command):
            raise src.SatException(_("Command '%s' does not exist") % command)
        
        # Print salomeTools version
        msg = "\n" + get_version() + "\n\n"
        
        # load the module
        module = self.get_module(command)

        # print the description of the command that is done in the command file
        if hasattr( module, "description" ) :
            msg += src.printcolors.printcHeader( _("Description:") )
            msg += '\n' + module.description() + '\n\n'

        # print the description of the command options
        if hasattr( module, "parser" ):
            msg += module.parser.get_help()

        msg += "\n -h, --help (boolean)\n          shows help on command.\n"
        return msg

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

##################################################################
def get_text_from_options(options):
    text_options = ""
    for attr in dir(options):
        if attr.startswith("__"):
            continue
        if options.__getattr__(attr) != None:
            option_contain = options.__getattr__(attr)
            if type(option_contain)==type([]):
                option_contain = ",".join(option_contain)
            if type(option_contain)==type(True):
                option_contain = ""
            text_options+= "--%s %s " % (attr, option_contain)
    return text_options
                

def get_version():
    '''
    get colorized salomeTools version (in src/internal_config/salomeTools.pyconf).
    returns string
    '''
    # read the config 
    cfgManager = CONFIG.ConfigManager()
    cfg = cfgManager.get_config()
    # print the key corresponding to salomeTools version
    msg = (src.printcolors.printcHeader( _("Version: ") ) + src.get_salometool_version(cfg))
    return msg


def get_help():
    '''
    get salomeTools general help.
    returns string
    '''
    msg = "\n" + get_version() + "\n\n"
    msg += src.printcolors.printcHeader( _("Usage: ") ) + \
          "sat [sat_options] <command> [application] [command_options]\n\n"

    msg += parser.get_help() + "\n"

    # display all the available commands.
    msg += src.printcolors.printcHeader(_("Available commands are:")) + "\n"
    for command in lCommand:
        msg += " - %s\n" % (command)

    msg += "\n"
    # Explain how to get the help for a specific command
    msg += src.printcolors.printcHeader(
        _("Get help for a specific command:")) + \
        "\n>> sat --help <command>\n"
    return msg

def write_exception(exc):
    '''write exception in case of error in a command
    
    :param exc exception: the exception to print
    '''
    sys.stderr.write("\n***** ")
    sys.stderr.write(src.printcolors.printcError("salomeTools ERROR:"))
    sys.stderr.write("\n" + str(exc) + "\n")


