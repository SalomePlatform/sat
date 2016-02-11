#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import shutil
import re

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('t', 'terminal', 'boolean', 'terminal', "Terminal log.")

def show_log_command_in_terminal(filePath, logger):
    '''Print the contain of filePath. It contains a command log in xml format.
    
    :param filePath: The command xml file from which extract the commands context and traces
    :logger Logger: the logging instance to use in order to print.  
    '''
    # Instantiate the readXmlFile class that reads xml files
    xmlRead = src.xmlManager.readXmlFile(filePath)
    # Get the attributes containing the context (user, OS, time, etc..)
    lAttrText = xmlRead.get_attrib_text('name')
    logger.write("\n", 1)
    # Print the context
    src.print_info(logger, lAttrText)
    # Get the traces
    command_traces = xmlRead.get_node_text('traces')
    # Print it if there is any
    if command_traces:
        logger.write(_("Here are the command traces :\n"), 1)
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
        rep = raw_input(_("Which one (enter or 0 to quit)? "))
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
    return _("Gives access to logs of salomeTools.")    

def run(args, runner, logger):
    '''method that is called when salomeTools is called with log parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)

    # get the log directory. If there is an application, it is in cfg.APPLICATION.out_dir, else in user directory
    logDir = runner.cfg.VARS.logDir

    # If the user asks for a terminal display
    if options.terminal:
        # Parse the log directory in order to find all the files corresponding to the commands
        lLogs = []
        for fileName in os.listdir(logDir):
            sExpr = "^[0-9]{8}_+[0-9]{6}_+.*.xml$"
            oExpr = re.compile(sExpr)
            if oExpr.search(fileName):
                lLogs.append(fileName)
        lLogs = sorted(lLogs)
        nb_logs = len(lLogs)
        index = 0
        # loop on all files and print it with date, time and command name 
        for t in lLogs:
            date_hour_cmd = t.split('_')
            date_not_formated = date_hour_cmd[0]
            date = "%s/%s/%s" % (date_not_formated[6:8], date_not_formated[4:6], date_not_formated[0:4] )
            hour_not_formated = date_hour_cmd[1]
            hour = "%s:%s:%s" % (hour_not_formated[0:2], hour_not_formated[2:4], hour_not_formated[4:6])
            cmd = date_hour_cmd[2][:-len('.xml')]
            
            num = src.printcolors.printcLabel("%2d" % (nb_logs - index))
            logger.write("%s: %13s %s %s\n" % (num, cmd, date, hour), 1, False)
            index += 1
        
        # ask the user what for what command he wants to be displayed
        x = -1
        while (x < 0):
            x = ask_value(nb_logs)
            if x > 0:
                index = len(lLogs) - int(x)
                # Show the log corresponding to the selected command call
                show_log_command_in_terminal(os.path.join(logDir, lLogs[index]), logger)                
                x = 0
        
        return 0
                    
    
    # Find the stylesheets Directory and files
    xslDir = os.path.join(runner.cfg.VARS.srcDir, 'xsl')
    xslCommand = os.path.join(xslDir, "command.xsl")
    xslHat = os.path.join(xslDir, "hat.xsl")
    imgLogo = os.path.join(xslDir, "LOGO-SAT.png")
    
    # copy the stylesheets in the log directory
    shutil.copy2(xslCommand, logDir)
    shutil.copy2(xslHat, logDir)
    shutil.copy2(imgLogo, logDir)
    
    # Create or update the hat xml that gives access to all the commands log files
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    if 'APPLICATION' in runner.cfg:
        src.xmlManager.update_hat_xml(runner.cfg.VARS.logDir, runner.cfg.VARS.application)
    else:
        src.xmlManager.update_hat_xml(runner.cfg.VARS.logDir)
    
    # open the hat xml in the user editor
    src.system.show_in_editor(runner.cfg.USER.browser, xmlHatFilePath)