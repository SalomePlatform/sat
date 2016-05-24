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

# get execution path
testdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(testdir, '..', '..'))
sys.path.append(os.path.join(testdir, '..', '_testTools'))
sys.path.append(os.path.join(testdir, '..', '..','commands'))

import src.product

from salomeTools import Sat
import HTMLTestRunner

class TestMakeinstall(unittest.TestCase):
    '''Test of the makeinstall command
    '''

    def test_makeinstall(self):
        '''Test the configure command without any option
        '''
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')
       
        sat.configure(appli + ' --product ' + product_name)
        
        sat.make(appli + ' --product ' + product_name)
        
        sat.makeinstall(appli + ' --product ' + product_name)
        
        if os.path.exists(expected_file_path):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_description(self):
        '''Test the sat -h make
        '''        

        OK = "KO"

        import makeinstall
        
        if "The makeinstall command executes the \"make install\" command" in makeinstall.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
