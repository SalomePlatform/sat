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
'''In this file are implemented the classes and method relative to the logging
'''

import sys
import os
import datetime
import re

import src
from . import printcolors
from . import xmlManager

logCommandFileExpression = "^[0-9]{8}_+[0-9]{6}_+.*\.xml$"

class Logger(object):
    '''Class to handle log mechanism.
    '''
    def __init__(self, config, silent_sysstd=False, all_in_terminal=False):
        '''Initialization
        
        :param config pyconf.Config: The global configuration.
        :param silent_sysstd boolean: if True, do not write anything
                                      in terminal.
        '''
        self.config = config
        self.default_level = 3
        self.silentSysStd = silent_sysstd
        
        # Construct xml log file location for sat prints.
        logFileName = config.VARS.datehour + "_" + config.VARS.command + ".xml"
        logFilePath = os.path.join(config.SITE.log.log_dir, logFileName)
        # Construct txt file location in order to log 
        # the external commands calls (cmake, make, git clone, etc...)
        txtFileName = config.VARS.datehour + "_" + config.VARS.command + ".txt"
        txtFilePath = os.path.join(config.SITE.log.log_dir, "OUT", txtFileName)
        
        src.ensure_path_exists(os.path.dirname(logFilePath))
        src.ensure_path_exists(os.path.dirname(txtFilePath))
        
        self.logFileName = logFileName
        self.logFilePath = logFilePath
        self.txtFileName = txtFileName
        self.txtFilePath = txtFilePath
        # Initialize xml instance and put first fields 
        # like beginTime, user, command, etc... 
        self.xmlFile = xmlManager.XmlLogFile(logFilePath, "SATcommand", 
                            attrib = {"application" : config.VARS.application})
        self.put_initial_xml_fields()
        # Initialize the txt file for reading
        self.logTxtFile = open(str(self.txtFilePath), 'w')
        if all_in_terminal:
            self.logTxtFile = sys.__stdout__
        
    def put_initial_xml_fields(self):
        '''Method called at class initialization : Put all fields 
           corresponding to the command context (user, time, ...)
        '''
        # command name
        self.xmlFile.add_simple_node("Site", attrib={"command" : 
                                                     self.config.VARS.command})
        # version of salomeTools
        self.xmlFile.append_node_attrib("Site", attrib={"satversion" : 
                                            self.config.INTERNAL.sat_version})
        # machine name on which the command has been launched
        self.xmlFile.append_node_attrib("Site", attrib={"hostname" : 
                                                    self.config.VARS.hostname})
        # Distribution of the machine
        self.xmlFile.append_node_attrib("Site", attrib={"OS" : 
                                                        self.config.VARS.dist})
        # The user that have launched the command
        self.xmlFile.append_node_attrib("Site", attrib={"user" : 
                                                        self.config.VARS.user})
        # The time when command was launched
        Y, m, dd, H, M, S = date_to_datetime(self.config.VARS.datehour)
        date_hour = "%2s/%2s/%4s %2sh%2sm%2ss" % (dd, m, Y, H, M, S)
        self.xmlFile.append_node_attrib("Site", attrib={"beginTime" : 
                                                        date_hour})
        # The application if any
        if "APPLICATION" in self.config:
            self.xmlFile.append_node_attrib("Site", 
                        attrib={"application" : self.config.VARS.application})
        # The initialization of the trace node
        self.xmlFile.add_simple_node("Log",text="")
        self.xmlFile.add_simple_node("OutLog",
                                    text=os.path.join("OUT", self.txtFileName))

    def write(self, message, level=None, screenOnly=False):
        '''the function used in the commands 
        that will print in the terminal and the log file.
        
        :param message str: The message to print.
        :param level int: The output level corresponding 
                          to the message 0 < level < 6.
        :param screenOnly boolean: if True, do not write in log file.
        '''
        # do not write message starting with \r to log file
        if not message.startswith("\r") and not screenOnly:
            self.xmlFile.append_node_text("Log", 
                                          printcolors.cleancolor(message))

        # get user or option output level
        current_output_verbose_level = self.config.USER.output_verbose_level
        if not ('isatty' in dir(sys.stdout) and sys.stdout.isatty()):
            # clean the message color if the terminal is redirected by user
            # ex: sat compile appli > log.txt
            message = printcolors.cleancolor(message)
        
        # Print message regarding the output level value
        if level:
            if level <= current_output_verbose_level and not self.silentSysStd:
                sys.stdout.write(message)
        else:
            if self.default_level <= current_output_verbose_level and not self.silentSysStd:
                sys.stdout.write(message)

    def error(self, message):
        '''Print an error.
        
        :param message str: The message to print.
        '''
        # Print in the log file
        self.xmlFile.append_node_text("traces", _('ERROR:') + message)

        # Print in the terminal and clean colors if the terminal 
        # is redirected by user
        if not ('isatty' in dir(sys.stderr) and sys.stderr.isatty()):
            sys.stderr.write(printcolors.printcError(_('ERROR:') + message))
        else:
            sys.stderr.write(_('ERROR:') + message)

    def flush(self):
        '''Flush terminal
        '''
        sys.stdout.flush()
        self.logTxtFile.flush()
        
    def end_write(self, attribute):
        '''Method called just after command end : Put all fields 
           corresponding to the command end context (time).
           Write the log xml file on the hard drive.
           And display the command to launch to get the log
        
        :param attribute dict: the attribute to add to the node "Site".
        '''       
        # Get current time (end of command) and format it
        dt = datetime.datetime.now()
        Y, m, dd, H, M, S = date_to_datetime(self.config.VARS.datehour)
        t0 = datetime.datetime(int(Y), int(m), int(dd), int(H), int(M), int(S))
        tf = dt
        delta = tf - t0
        total_time = timedelta_total_seconds(delta)
        hours = int(total_time / 3600)
        minutes = int((total_time - hours*3600) / 60)
        seconds = total_time - hours*3600 - minutes*60
        # Add the fields corresponding to the end time
        # and the total time of command
        endtime = dt.strftime('%d/%Y/%m %Hh%Mm%Ss')
        self.xmlFile.append_node_attrib("Site", attrib={"endTime" : endtime})
        self.xmlFile.append_node_attrib("Site", 
                attrib={"TotalTime" : "%ih%im%is" % (hours, minutes, seconds)})
        
        # Add the attribute passed to the method
        self.xmlFile.append_node_attrib("Site", attrib=attribute)
        
        # Call the method to write the xml file on the hard drive
        self.xmlFile.write_tree(stylesheet = "command.xsl")
        
        # Dump the config in a pyconf file in the log directory
        logDir = self.config.SITE.log.log_dir
        dumpedPyconfFileName = (self.config.VARS.datehour 
                                + "_" 
                                + self.config.VARS.command 
                                + ".pyconf")
        dumpedPyconfFilePath = os.path.join(logDir, 'OUT', dumpedPyconfFileName)
        f = open(dumpedPyconfFilePath, 'w')
        self.config.__save__(f)
        f.close()
        

def date_to_datetime(date):
    '''Little method that gets year, mon, day, hour , 
       minutes and seconds from a str in format YYYYMMDD_HHMMSS
    
    :param date str: The date in format YYYYMMDD_HHMMSS
    :return: the same date and time in separate variables.
    :rtype: (str,str,str,str,str,str)
    '''
    Y = date[:4]
    m = date[4:6]
    dd = date[6:8]
    H = date[9:11]
    M = date[11:13]
    S = date[13:15]
    return Y, m, dd, H, M, S

def timedelta_total_seconds(timedelta):
    '''Little method to replace total_seconds from 
       datetime module in order to be compatible with old python versions
    
    :param timedelta datetime.timedelta: The delta between two dates
    :return: The number of seconds corresponding to timedelta.
    :rtype: float
    '''
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6
        
def show_command_log(logFilePath, cmd, application, notShownCommands):
    '''Used in updateHatXml. Determine if the log xml file logFilePath 
       has to be shown or not in the hat log.
    
    :param logFilePath str: the path to the command xml log file
    :param cmd str: the command of the log file
    :param application str: the application passed as parameter 
                            to the salomeTools command
    :param notShownCommands list: the list of commands 
                                  that are not shown by default
    
    :return: True if cmd is not in notShownCommands and the application 
             in the log file corresponds to application
    :rtype: boolean
    '''
    # When the command is not in notShownCommands, no need to go further :
    # Do not show
    if cmd in notShownCommands:
        return False, None
 
    # Get the application of the log file
    logFileXml = src.xmlManager.ReadXmlFile(logFilePath)
    if 'application' in logFileXml.xmlroot.keys():
        appliLog = logFileXml.xmlroot.get('application')
        # if it corresponds, then the log has to be shown
        if appliLog == application:
            return True, appliLog
        elif application != 'None':
            return False, appliLog
        
        return True, appliLog
    
    if application == 'None':
            return True, None    
        
    return False, None

def list_log_file(dirPath, expression):
    '''Find all files corresponding to expression in dirPath
    
    :param dirPath str: the directory where to search the files
    :param expression str: the regular expression of files to find
    :return: the list of files path and informations about it
    :rtype: list
    '''
    lRes = []
    for fileName in os.listdir(dirPath):
        # YYYYMMDD_HHMMSS_namecmd.xml
        sExpr = expression
        oExpr = re.compile(sExpr)
        if oExpr.search(fileName):
            # get date and hour and format it
            date_hour_cmd = fileName.split('_')
            date_not_formated = date_hour_cmd[0]
            date = "%s/%s/%s" % (date_not_formated[6:8], 
                                 date_not_formated[4:6], date_not_formated[0:4] )
            hour_not_formated = date_hour_cmd[1]
            hour = "%s:%s:%s" % (hour_not_formated[0:2], 
                                 hour_not_formated[2:4], hour_not_formated[4:6])
            cmd = date_hour_cmd[2][:-len('.xml')]
            lRes.append((os.path.join(dirPath, fileName), 
                         date_not_formated, date, hour_not_formated, hour, cmd))
    return lRes

def update_hat_xml(logDir, application=None, notShownCommands = []):
    '''Create the xml file in logDir that contain all the xml file 
       and have a name like YYYYMMDD_HHMMSS_namecmd.xml
    
    :param logDir str: the directory to parse
    :param application str: the name of the application if there is any
    '''
    # Create an instance of XmlLogFile class to create hat.xml file
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    xmlHat = src.xmlManager.XmlLogFile(xmlHatFilePath,
                                    "LOGlist", {"application" : application})
    # parse the log directory to find all the command logs, 
    # then add it to the xml file
    lLogFile = list_log_file(logDir, logCommandFileExpression)
    for filePath, _, date, _, hour, cmd in lLogFile:
        showLog, cmdAppli = show_command_log(filePath, cmd,
                                              application, notShownCommands)
        #if cmd not in notShownCommands:
        if showLog:
            # add a node to the hat.xml file
            xmlHat.add_simple_node("LogCommand", 
                                   text=os.path.basename(filePath), 
                                   attrib = {"date" : date, 
                                             "hour" : hour, 
                                             "cmd" : cmd, 
                                             "application" : cmdAppli})
    
    # Write the file on the hard drive
    xmlHat.write_tree('hat.xsl')