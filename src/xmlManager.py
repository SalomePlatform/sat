#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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
import re

import src
from . import ElementTree as etree

class xmlLogFile(object):
    '''Class to manage writing in salomeTools xml log file
    '''
    def __init__(self, filePath, rootname, attrib = {}):
        '''Initialization
        
        :param filePath str: The path to the file where to write the log file
        :param rootname str: The name of the root node of the xml file
        :param attrib dict: the dictionary that contains the attributes and value of the root node
        '''
        # Initialize the filePath and ensure that the directory that contain the file exists (make it if necessary)
        self.logFile = filePath
        src.ensure_path_exists(os.path.dirname(filePath))
        # Initialize the field that contain the xml in memory
        self.xmlroot = etree.Element(rootname, attrib = attrib)
    
    def write_tree(self, stylesheet=None):
        '''Write the xml tree in the log file path. Add the stylesheet if asked.
        
        :param stylesheet str: The stylesheet to apply to the xml file
        '''
        f = open(self.logFile, 'w')
        f.write("<?xml version='1.0' encoding='utf-8'?>\n")
        if stylesheet:
            f.write("<?xml-stylesheet type='text/xsl' href='%s'?>\n" % stylesheet)    
        f.write(etree.tostring(self.xmlroot, encoding='utf-8'))
        f.close()  
        
    def add_simple_node(self, node_name, text=None, attrib={}):
        '''Add a node with some attibutes and text to the root node.
        
        :param node_name str: the name of the node to add
        :param text str: the text of the node
        :param attrib dict: the dictionary containing the attribute of the new node
        '''
        n = etree.Element(node_name, attrib=attrib)
        n.text = text
        self.xmlroot.append(n)
        return n
    
    def append_node_text(self, node_name, text):
        '''Append a new text to the node that has node_name as name
        
        :param node_name str: The name of the node on which append text
        :param text str: The text to append
        '''
        # find the corresponding node
        for field in self.xmlroot:
            if field.tag == node_name:
                # append the text
                field.text += text

    def append_node_attrib(self, node_name, attrib):
        '''Append a new attributes to the node that has node_name as name
        
        :param node_name str: The name of the node on which append text
        :param attrib dixt: The attrib to append
        '''
        self.xmlroot.find(node_name).attrib.update(attrib)

class readXmlFile(object):
    '''Class to manage reading of an xml log file
    '''
    def __init__(self, filePath):
        '''Initialization
        
        :param filePath str: The xml file to be read
        '''
        self.filePath = filePath
        etree_inst = etree.parse(filePath)
        self.xmlroot = etree_inst.parse(filePath)

    def getRootAttrib(self):
        '''Get the attibutes of the self.xmlroot
        
        :return: The attributes of the root node
        :rtype: dict
        '''
        return self.xmlroot.attrib
    
    def get_attrib(self, node_name):
        '''Get the attibutes of the node node_name in self.xmlroot
        
        :param node_name str: the name of the node
        :return: the attibutes of the node node_name in self.xmlroot
        :rtype: dict
        '''
        return self.xmlroot.find(node_name).attrib
    
    def get_node_text(self, node):
        '''Get the text of the first node that has name that corresponds to the parameter node
        
        :param node str: the name of the node from which get the text
        :return: the text of the first node that has name that corresponds to the parameter node
        :rtype: str
        '''
        # Loop on all root nodes
        for field in self.xmlroot:
            if field.tag == node:
                return field.text
        return ''

def showcommandLog(logFilePath, cmd, application, notShownCommands):
    '''Used in updateHatXml. Determine if the log xml file logFilePath has to be shown or not in the hat log.
    
    :param logFilePath str: the path to the command xml log file
    :param cmd str: the command of the log file
    :param application str: the application passed as parameter to the salomeTools command
    :param notShownCommands list: the list of commands that are not shown by default
    
    :return: True if cmd is not in notShownCommands and the application in the log file corresponds to application
    :rtype: boolean
    '''
    # When the command is not in notShownCommands, no need to go further. Do not show
    if cmd in notShownCommands:
        return False, None
 
    # Get the application of the log file
    logFileXml = readXmlFile(logFilePath)
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
    

def update_hat_xml(logDir, application=None, notShownCommands = []):
    '''Create the xml file in logDir that contain all the xml file and have a name like YYYYMMDD_HHMMSS_namecmd.xml
    
    :param logDir str: the directory to parse
    :param application str: the name of the application if there is any
    '''
    # Create an instance of xmlLogFile class to create hat.xml file
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    xmlHat = xmlLogFile(xmlHatFilePath,  "LOGlist", {"application" : application})
    # parse the log directory to find all the command logs, then add it to the xml file
    for fileName in os.listdir(logDir):
        # YYYYMMDD_HHMMSS_namecmd.xml
        sExpr = "^[0-9]{8}_+[0-9]{6}_+.*\.xml$"
        oExpr = re.compile(sExpr)
        if oExpr.search(fileName):
            # get date and hour and format it
            date_hour_cmd = fileName.split('_')
            date_not_formated = date_hour_cmd[0]
            date = "%s/%s/%s" % (date_not_formated[6:8], date_not_formated[4:6], date_not_formated[0:4] )
            hour_not_formated = date_hour_cmd[1]
            hour = "%s:%s:%s" % (hour_not_formated[0:2], hour_not_formated[2:4], hour_not_formated[4:6])
            cmd = date_hour_cmd[2][:-len('.xml')]
            showLog, cmdAppli = showcommandLog(os.path.join(logDir, fileName), cmd, application, notShownCommands)
            #if cmd not in notShownCommands:
            if showLog:
                # add a node to the hat.xml file
                xmlHat.add_simple_node("LogCommand", text=fileName, attrib = {"date" : date, "hour" : hour, "cmd" : cmd, "application" : cmdAppli})
    
    # Write the file on the hard drive
    xmlHat.write_tree('hat.xsl')