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

import src
from . import printcolors
from . import xmlManager

class Logger(object):
    '''Class that handle log mechanism
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
        
        self.xmlFile = xmlManager.xmlLogFile(logFilePath, config.VARS.command)
        self.putInitialXMLFields()
        
    def putInitialXMLFields(self):
        self.xmlFile.add_simple_node("field", text=self.config.VARS.command , attrib={"name" : "command"})
        self.xmlFile.add_simple_node("field", text=self.config.INTERNAL.sat_version , attrib={"name" : "satversion"})
        self.xmlFile.add_simple_node("field", text=self.config.VARS.hostname , attrib={"name" : "hostname"})
        self.xmlFile.add_simple_node("field", text=self.config.VARS.dist , attrib={"name" : "OS"})
        self.xmlFile.add_simple_node("field", text=self.config.VARS.user , attrib={"name" : "user"})
        self.xmlFile.add_simple_node("field", text=self.config.VARS.datehour , attrib={"name" : "beginTime"})
        self.xmlFile.add_simple_node("traces",text="")

    def write(self, message, level=None, screenOnly=False):
        '''the function used in the commands that will print in the terminal and the log file.
        
        :param message str: The message to print.
        :param level int: The output level corresponding to the message 0 < level < 6.
        :param screenOnly boolean: if True, do not write in log file.
        '''
        # do not write message starting with \r to log file
        if not message.startswith("\r") and not screenOnly:
            self.xmlFile.append_node("traces", printcolors.cleancolor(message))

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
        self.xmlFile.append_node("traces", _('ERROR:') + message)

        # Print in the terminal and clean colors if the terminal is redirected by user
        if not ('isatty' in dir(sys.stderr) and sys.stderr.isatty()):
            sys.stderr.write(printcolors.printcError(_('ERROR:') + message))
        else:
            sys.stderr.write(_('ERROR:') + message)

    def flush(self):
        '''Flush terminal
        '''
        sys.stdout.flush()
        
    def endWrite(self):
        self.xmlFile.write_tree()
