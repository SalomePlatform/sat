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
        self.logFile = filePath
        src.ensure_path_exists(os.path.dirname(filePath))
        self.xmlroot = etree.Element(rootname, attrib = attrib)
    
    def write_tree(self, stylesheet=None):
        f = open(self.logFile, 'w')
        f.write("<?xml version='1.0' encoding='utf-8'?>\n")
        if stylesheet:
            f.write("<?xml-stylesheet type='text/xsl' href='%s'?>\n" % stylesheet)    
        f.write(etree.tostring(self.xmlroot, encoding='utf-8'))
        f.close()  
        
    def add_simple_node(self, node_name, text=None, attrib={}):
        n = etree.Element(node_name, attrib=attrib)
        n.text = text
        self.xmlroot.append(n)
        return n
    
    def append_node(self, node_name, text):
        for field in self.xmlroot:
            if field.tag == node_name:
                field.text += text
                
def update_hat_xml(logDir, application=None):
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    if application:
        xmlHat = xmlLogFile(xmlHatFilePath,  "LOGlist", {"application" : application})
    else:
        xmlHat = xmlLogFile(xmlHatFilePath,  "LOGlist", {"application" : "NO"})
          
    for fileName in os.listdir(logDir):
        sExpr = "^[0-9]{8}_+[0-9]{6}_+[A-Za-z0-9]*.xml$"
        oExpr = re.compile(sExpr)
        if oExpr.search(fileName):
            date_hour_cmd = fileName.split('_')
            date_not_formated = date_hour_cmd[0]
            date = "%s/%s/%s" % (date_not_formated[6:8], date_not_formated[4:6], date_not_formated[0:4] )
            hour_not_formated = date_hour_cmd[1]
            hour = "%s:%s:%s" % (hour_not_formated[0:2], hour_not_formated[2:4], hour_not_formated[4:6])
            cmd = date_hour_cmd[2][:-len('.xml')]
        
            xmlHat.add_simple_node("LogCommand", text=fileName, attrib = {"date" : date, "hour" : hour, "cmd" : cmd})
    
    xmlHat.write_tree('hat.xsl')