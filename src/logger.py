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

import sys
import os
import datetime

import src
from . import printcolors
from . import xmlManager

class Logger(object):
    '''Class to handle log mechanism
    '''
    def __init__(self, config, silent_sysstd=False):
        '''Initialization
        
        :param config pyconf.Config: The global configuration.
        :param silent_sysstd boolean: if True, do not write anything in terminal.
        '''
        self.config = config
        self.default_level = 3
        self.silentSysStd = silent_sysstd
        
        # Construct log file location. There are two cases. With an application an without any application.
        logFileName = config.VARS.datehour + "_" + config.VARS.command + ".xml"
        if 'APPLICATION' in config:
            logFilePath = os.path.join(config.APPLICATION.out_dir, 'LOGS', logFileName)
        else:
            logFilePath = os.path.join(config.VARS.personalDir, 'LOGS', logFileName)
        src.ensure_path_exists(os.path.dirname(logFilePath))
        
        self.logFileName = logFileName
        self.logFilePath = logFilePath   
        self.xmlFile = xmlManager.xmlLogFile(logFilePath, "SATcommand", attrib = {"command" : config.VARS.command})
        self.putInitialXMLFields()
        
    def putInitialXMLFields(self):
        '''Method called at class initialization : Put all fields corresponding to the command context (user, time, ...)
        '''
        # command name
        self.xmlFile.add_simple_node("Site", attrib={"command" : self.config.VARS.command})
        # version of salomeTools
        self.xmlFile.append_node_attrib("Site", attrib={"satversion" : self.config.INTERNAL.sat_version})
        # machine name on which the command has been launched
        self.xmlFile.append_node_attrib("Site", attrib={"hostname" : self.config.VARS.hostname})
        # Distribution of the machine
        self.xmlFile.append_node_attrib("Site", attrib={"OS" : self.config.VARS.dist})
        # The user that have launched the command
        self.xmlFile.append_node_attrib("Site", attrib={"user" : self.config.VARS.user})
        # The time when command was launched
        Y, m, dd, H, M, S = date_to_datetime(self.config.VARS.datehour)
        date_hour = "%2s/%2s/%4s %2sh%2sm%2ss" % (dd, m, Y, H, M, S)
        self.xmlFile.append_node_attrib("Site", attrib={"beginTime" : date_hour})
        # The initialization of the trace node
        self.xmlFile.add_simple_node("Log",text="")

    def write(self, message, level=None, screenOnly=False):
        '''the function used in the commands that will print in the terminal and the log file.
        
        :param message str: The message to print.
        :param level int: The output level corresponding to the message 0 < level < 6.
        :param screenOnly boolean: if True, do not write in log file.
        '''
        # do not write message starting with \r to log file
        if not message.startswith("\r") and not screenOnly:
            self.xmlFile.append_node_text("Log", printcolors.cleancolor(message))

        # get user or option output level
        current_output_level = self.config.USER.output_level
        if not ('isatty' in dir(sys.stdout) and sys.stdout.isatty()):
            # clean the message color if the terminal is redirected by user
            # ex: sat compile appli > log.txt
            message = printcolors.cleancolor(message)
        
        # Print message regarding the output level value
        if level:
            if level <= current_output_level and not self.silentSysStd:
                sys.stdout.write(message)
        else:
            if self.default_level <= current_output_level and not self.silentSysStd:
                sys.stdout.write(message)

    def error(self, message):
        '''Print an error.
        
        :param message str: The message to print.
        '''
        # Print in the log file
        self.xmlFile.append_node_text("traces", _('ERROR:') + message)

        # Print in the terminal and clean colors if the terminal is redirected by user
        if not ('isatty' in dir(sys.stderr) and sys.stderr.isatty()):
            sys.stderr.write(printcolors.printcError(_('ERROR:') + message))
        else:
            sys.stderr.write(_('ERROR:') + message)

    def flush(self):
        '''Flush terminal
        '''
        sys.stdout.flush()
        
    def endWrite(self, attribute):
        '''Method called just after command end : Put all fields corresponding to the command end context (time).
        Write the log xml file on the hard drive.
        And display the command to launch to get the log
        '''
        # Print the command to launch to get the log, regarding the fact that there an application or not
        self.write(_('\nTap the following command to get the log :\n'), screenOnly=True)
        if 'APPLICATION' in self.config:
            self.write('%s/sat log %s\n' % (self.config.VARS.salometoolsway, self.config.VARS.application), screenOnly=True)
        else:
            self.write('%s/sat log\n' % self.config.VARS.salometoolsway, screenOnly=True)
        
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
        # Add the fields corresponding to the end time and the total time of command
        endtime = dt.strftime('%d/%Y/%m %Hh%Mm%Ss')
        self.xmlFile.append_node_attrib("Site", attrib={"endTime" : endtime})
        self.xmlFile.append_node_attrib("Site", attrib={"TotalTime" : "%ih%im%is" % (hours, minutes, seconds)})
        
        # Add the attribute passed to the method
        self.xmlFile.append_node_attrib("Site", attrib=attribute)
        
        # Call the method to write the xml file on the hard drive
        self.xmlFile.write_tree(stylesheet = "command.xsl")
        
        # Update the hat xml (that shows all logs) in order to make the new log visible on the main log page)
        if 'APPLICATION' in self.config:
            src.xmlManager.update_hat_xml(self.config.VARS.logDir, self.config.VARS.application)
        else:
            src.xmlManager.update_hat_xml(self.config.VARS.logDir)

def date_to_datetime(date):
    '''Little method that gets year, mon, day, hour , minutes and seconds from a str in format YYYYMMDD_HHMMSS
    
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
    '''Little method to replace total_seconds from datetime module in order to be compatible with old python versions
    
    :param timedelta datetime.timedelta: The delta between two dates
    :return: The number of seconds corresponding to timedelta.
    :rtype: float
    '''
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6