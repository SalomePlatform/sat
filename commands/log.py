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

import os
import shutil
import re
import glob

# Compatibility python 2/3 for input function
# input stays input for python 3 and input = raw_input for python 2
try: 
    input = raw_input
except NameError: 
    pass

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('t', 'terminal', 'boolean', 'terminal', "Optional: "
                  "Terminal log.")
parser.add_option('l', 'last', 'boolean', 'last', "Show the log of the last "
                  "Optional: launched command.")
parser.add_option('f', 'full', 'boolean', 'full', "Optional: Show the logs of "
                  "ALL the launched commands.")
parser.add_option('c', 'clean', 'int', 'clean', "Optional: Erase the n most "
                  "ancient log files.")

def get_last_log_file(logDir, notShownCommands):
    '''Used in case of last option. Get the last log command file path.
    
    :param logDir str: The directory where to search the log files
    :param notShownCommands list: the list of commands to ignore
    :return: the path to the last log file
    :rtype: str
    '''
    last = (_, 0)
    for fileName in os.listdir(logDir):
        # YYYYMMDD_HHMMSS_namecmd.xml
        sExpr = src.logger.logCommandFileExpression
        oExpr = re.compile(sExpr)
        if oExpr.search(fileName):
            # get date and hour and format it
            date_hour_cmd = fileName.split('_')
            datehour = date_hour_cmd[0] + date_hour_cmd[1]
            cmd = date_hour_cmd[2][:-len('.xml')]
            if cmd in notShownCommands:
                continue
            if int(datehour) > last[1]:
                last = (fileName, int(datehour))
    return os.path.join(logDir, last[0])

def remove_log_file(filePath, logger):
    '''if it exists, print a warning and remove the input file
    
    :param filePath: the path of the file to delete
    :param logger Logger: the logger instance to use for the print 
    '''
    if os.path.exists(filePath):
        logger.write(src.printcolors.printcWarning("Removing ")
                     + filePath + "\n", 5)
        os.remove(filePath)

def print_log_command_in_terminal(filePath, logger):
    '''Print the contain of filePath. It contains a command log in xml format.
    
    :param filePath: The command xml file from which extract the commands 
                     context and traces
    :param logger Logger: the logging instance to use in order to print.  
    '''
    logger.write(_("Reading ") + src.printcolors.printcHeader(filePath) + "\n", 5)
    # Instantiate the ReadXmlFile class that reads xml files
    xmlRead = src.xmlManager.ReadXmlFile(filePath)
    # Get the attributes containing the context (user, OS, time, etc..)
    dAttrText = xmlRead.get_attrib('Site')
    # format dAttrText and print the context
    lAttrText = []
    for attrib in dAttrText:
        lAttrText.append((attrib, dAttrText[attrib]))
    logger.write("\n", 1)
    src.print_info(logger, lAttrText)
    # Get the traces
    command_traces = xmlRead.get_node_text('Log')
    # Print it if there is any
    if command_traces:
        logger.write(src.printcolors.printcHeader(
                                    _("Here are the command traces :\n")), 1)
        logger.write(command_traces, 1)
        logger.write("\n", 1)

def ask_value(nb):
    '''Ask for an int n. 0<n<nb
    
    :param nb int: The maximum value of the value to be returned by the user.
    :return: the value entered by the user. Return -1 if it is not as expected
    :rtype: int
    '''
    try:
        # ask for a value
        rep = input(_("Which one (enter or 0 to quit)? "))
        # Verify it is on the right range
        if len(rep) == 0:
            x = 0
        else:
            x = int(rep)
            if x > nb:
                x = -1
    except:
        x = -1
    
    return x

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the log command description.
    :rtype: str
    '''
    return _("Gives access to the logs produced by the salomeTools commands.\n"
             "\nexample:\nsat log")    

def run(args, runner, logger):
    '''method that is called when salomeTools is called with log parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)

    # get the log directory. 
    logDir = runner.cfg.USER.log_dir
    
    # Print a header
    nb_files_log_dir = len(glob.glob(os.path.join(logDir, "*")))
    info = [("log directory", logDir), 
            ("number of log files", nb_files_log_dir)]
    src.print_info(logger, info)
    
    # If the clean options is invoked, 
    # do nothing but deleting the concerned files.
    if options.clean:
        nbClean = options.clean
        # get the list of files to remove
        lLogs = src.logger.list_log_file(logDir, 
                                         src.logger.logCommandFileExpression)
        nbLogFiles = len(lLogs)
        # Delete all if the invoked number is bigger than the number of log files
        if nbClean > nbLogFiles:
            nbClean = nbLogFiles
        # Get the list to delete and do the removing
        lLogsToDelete = sorted(lLogs)[:nbClean]
        for filePath, __, __, __, __, __, __ in lLogsToDelete:
            # remove the xml log file
            remove_log_file(filePath, logger)
            # remove also the corresponding txt file in OUT directory
            txtFilePath = os.path.join(os.path.dirname(filePath), 
                            'OUT', 
                            os.path.basename(filePath)[:-len('.xml')] + '.txt')
            remove_log_file(txtFilePath, logger)
            # remove also the corresponding pyconf (do not exist 2016-06) 
            # file in OUT directory
            pyconfFilePath = os.path.join(os.path.dirname(filePath), 
                            'OUT', 
                            os.path.basename(filePath)[:-len('.xml')] + '.pyconf')
            remove_log_file(pyconfFilePath, logger)

        
        logger.write(src.printcolors.printcSuccess("OK\n"))
        logger.write("%i logs deleted.\n" % nbClean)
        return 0 

    # determine the commands to show in the hat log
    notShownCommands = runner.cfg.INTERNAL.log.not_shown_commands
    if options.full:
        notShownCommands = []

    # Find the stylesheets Directory and files
    xslDir = os.path.join(runner.cfg.VARS.srcDir, 'xsl')
    xslCommand = os.path.join(xslDir, "command.xsl")
    xslHat = os.path.join(xslDir, "hat.xsl")
    xsltest = os.path.join(xslDir, "test.xsl")
    imgLogo = os.path.join(xslDir, "LOGO-SAT.png")
    
    # copy the stylesheets in the log directory
    shutil.copy2(xslCommand, logDir)
    shutil.copy2(xslHat, logDir)
    src.ensure_path_exists(os.path.join(logDir, "TEST"))
    shutil.copy2(xsltest, os.path.join(logDir, "TEST"))
    shutil.copy2(imgLogo, logDir)

    # If the last option is invoked, just, show the last log file
    if options.last:
        lastLogFilePath = get_last_log_file(logDir, notShownCommands)        
        if options.terminal:
            # Show the log corresponding to the selected command call
            print_log_command_in_terminal(lastLogFilePath, logger)
        else:
            # open the log xml file in the user editor
            src.system.show_in_editor(runner.cfg.USER.browser, 
                                      lastLogFilePath, logger)
        return 0

    # If the user asks for a terminal display
    if options.terminal:
        # Parse the log directory in order to find 
        # all the files corresponding to the commands
        lLogs = src.logger.list_log_file(logDir, 
                                         src.logger.logCommandFileExpression)
        lLogsFiltered = []
        for filePath, __, date, __, hour, cmd in lLogs:
            showLog, cmdAppli = src.logger.show_command_log(filePath, cmd, 
                                runner.cfg.VARS.application, notShownCommands)
            if showLog:
                lLogsFiltered.append((filePath, date, hour, cmd, cmdAppli))
            
        lLogsFiltered = sorted(lLogsFiltered)
        nb_logs = len(lLogsFiltered)
        index = 0
        # loop on all files and print it with date, time and command name 
        for __, date, hour, cmd, cmdAppli in lLogsFiltered:          
            num = src.printcolors.printcLabel("%2d" % (nb_logs - index))
            logger.write("%s: %13s %s %s %s\n" % 
                         (num, cmd, date, hour, cmdAppli), 1, False)
            index += 1
        
        # ask the user what for what command he wants to be displayed
        x = -1
        while (x < 0):
            x = ask_value(nb_logs)
            if x > 0:
                index = len(lLogsFiltered) - int(x)
                # Show the log corresponding to the selected command call
                print_log_command_in_terminal(lLogsFiltered[index][0], logger)                
                x = 0
        
        return 0
                    
    # Create or update the hat xml that gives access to all the commands log files
    logger.write(_("Generating the hat log file (can be long) ... "), 3)
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    src.logger.update_hat_xml(runner.cfg.USER.log_dir, 
                              application = runner.cfg.VARS.application, 
                              notShownCommands = notShownCommands)
    logger.write(src.printcolors.printc("OK"), 3)
    logger.write("\n", 3)
    
    # open the hat xml in the user editor
    logger.write(_("\nOpening the log file\n"), 3)
    src.system.show_in_editor(runner.cfg.USER.browser, xmlHatFilePath, logger)
    return 0