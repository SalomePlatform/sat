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

import unittest
import os
import sys
import shutil

# get execution path
testdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(testdir, '..', '..'))
sys.path.append(os.path.join(testdir, '..', '_testTools'))
sys.path.append(os.path.join(testdir, '..', '..','commands'))

from tools import outRedirection

import src.product

from salomeTools import Sat
import HTMLTestRunner

class TestSource(unittest.TestCase):
    '''Test of the source command
    '''
    
    def test_source_archive(self):
        '''Test the source command with archive product
        '''
        appli = 'appli-test'
        product_name = 'PRODUCT_ARCHIVE'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_file_path = os.path.join(expected_src_dir, 'my_test_file.txt')
        expected_text = 'HELLO WORLD\n'

        f = open(expected_file_path, 'r')
        text = f.read()

        # pyunit method to compare 2 str
        self.assertEqual(text, expected_text)
        
    def test_source_git(self):
        '''Test the source command with git product
        '''
        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_file_path = os.path.join(expected_src_dir, 'my_test_file.txt')
        expected_text = 'HELLO WORLD\n'

        f = open(expected_file_path, 'r')
        text = f.read()

        # pyunit method to compare 2 str
        self.assertEqual(text, expected_text)

    def test_source_cvs(self):
        '''Test the source command with cvs product
        '''
        appli = 'appli-test'
        product_name = 'PRODUCT_CVS'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_file_path = os.path.join(expected_src_dir, 'README.FIRST.txt')
        expected_text = 'Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE\n'

        f = open(expected_file_path, 'r')
        text = f.readlines()[0]

        # pyunit method to compare 2 str
        self.assertEqual(text, expected_text)
    
    """
    def test_source_svn(self):
        '''Test the source command with svn product
        '''
        OK = 'KO'
        
        appli = 'appli-test'
        product_name = 'PRODUCT_SVN'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_file_path = os.path.join(expected_src_dir, 'scripts', 'README')
        expected_text = 'this directory contains scripts used by salomeTool'

        f = open(expected_file_path, 'r')
        text = f.readlines()[0]
        
        if expected_text in text:
            OK = 'OK'
         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')
    """

    def test_source_native(self):
        '''Test the source command with native product
        '''
        OK = 'KO'
        
        appli = 'appli-test'
        product_name = 'PRODUCT_NATIVE'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = os.path.join(sat.cfg.APPLICATION.out_dir, 'SOURCES', product_name)
        if not os.path.exists(expected_src_dir):
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_source_fixed(self):
        '''Test the source command with fixed product
        '''
        OK = 'KO'
        
        appli = 'appli-test'
        product_name = 'PRODUCT_FIXED'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).install_dir

        if os.path.exists(expected_src_dir):
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')
        
    def test_source_unknown(self):
        '''Test the source command with unknown product
        '''
        OK = 'KO'

        # output redirection
        my_out = outRedirection()

        appli = 'appli-test'
        product_name = 'PRODUCT_UNKNOWN'

        sat = Sat()
        sat.source(appli + ' --product ' + product_name)

        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()

        if "Unknown get source method" in res:
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_source_dev(self):
        '''Test the source command with a product in dev mode
        '''
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_DEV'

        sat = Sat()
               
        sat.config(appli)
        
        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_file_path = os.path.join(expected_src_dir, 'my_test_file.txt')
        expected_text = 'HELLO WORLD\n'
        
        if os.path.exists(expected_src_dir):
            shutil.rmtree(expected_src_dir)
        
        sat.source(appli + ' --product ' + product_name)
        
        f = open(expected_file_path, 'r')
        text = f.readlines()[0]
        OK1 = 'KO'
        if text == expected_text:
            OK1 = 'OK'

        # output redirection
        my_out = outRedirection()
        
        sat.source(appli + ' --product ' + product_name)
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()

        OK2 = 'KO'
        if "source directory already exists" in res:
            OK2 = 'OK'        

        # output redirection
        my_out = outRedirection()
        
        sat.source(appli + ' --product ' + product_name + ' --force')
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()

        OK3 = 'KO'
        if "source directory already exists" not in res:
            OK3 = 'OK'         

        if (OK1, OK2, OK3)==('OK', 'OK', 'OK'):
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_description(self):
        '''Test the sat -h source
        '''        

        OK = "KO"

        import source
        
        if "gets the sources of the application" in source.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
