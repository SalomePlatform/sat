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

import src

from salomeTools import Sat
import HTMLTestRunner

class TestPrepare(unittest.TestCase):
    '''Test of the prepare command
    '''

    def test_prepare_dev(self):
        '''Test the prepare command with a product in dev mode
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
        
        sat.prepare(appli + ' --product ' + product_name)
        
        f = open(expected_file_path, 'r')
        text = f.readlines()[0]
        if text == expected_text:
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_prepare_all(self):
        '''Test the prepare command with all products
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
        
        sat.prepare(appli)
        
        f = open(expected_file_path, 'r')
        text = f.readlines()[0]
        if text == expected_text:
            OK = 'OK'

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_prepare_option_sample_and_force(self):
        '''Test the prepare command with all products
        '''
        OK = 'KO'

        appli = 'appli-test'

        sat = Sat()
        sat.config(appli)
       
        try:
            sat.prepare(appli + " --force --force_patch")
            OK = 'OK'
        except:
            pass

        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_description(self):
        '''Test the sat -h prepare
        '''        

        OK = "KO"

        import prepare
        
        if "The prepare command gets the sources" in prepare.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
