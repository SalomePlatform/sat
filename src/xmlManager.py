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

import src
from . import ElementTree as etree

class XmlLogFile(object):
    '''Class to manage writing in salomeTools xml log file
    '''
    def __init__(self, filePath, rootname, attrib = {}):
        '''Initialization
        
        :param filePath str: The path to the file where to write the log file
        :param rootname str: The name of the root node of the xml file
        :param attrib dict: the dictionary that contains the attributes 
                            and value of the root node
        '''
        # Initialize the filePath and ensure that the directory 
        # that contain the file exists (make it if necessary)
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
            f.write("<?xml-stylesheet type='text/xsl' href='%s'?>\n" % 
                    stylesheet)    
        f.write(etree.tostring(self.xmlroot, encoding='utf-8'))
        f.close()  
        
    def add_simple_node(self, node_name, text=None, attrib={}):
        '''Add a node with some attibutes and text to the root node.
        
        :param node_name str: the name of the node to add
        :param text str: the text of the node
        :param attrib dict: the dictionary containing the 
                            attribute of the new node
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
        attrib = self.xmlroot.find(node_name).attrib
        # To be python 3 compatible, convert bytes to str if there are any
        fixedAttrib = {}
        for k in attrib.keys():
            if isinstance(k, bytes):
                key = k.decode()
            else:
                key = k
            if isinstance(attrib[k], bytes):
                value = attrib[k].decode()
            else:
                value = attrib[k]
            fixedAttrib[key] = value
        return fixedAttrib
    
    def get_node_text(self, node):
        '''Get the text of the first node that has name 
           that corresponds to the parameter node
        
        :param node str: the name of the node from which get the text
        :return: the text of the first node that has name 
                 that corresponds to the parameter node
        :rtype: str
        '''
        return self.xmlroot.find(node).text
