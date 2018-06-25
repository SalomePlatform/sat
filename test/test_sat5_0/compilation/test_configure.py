#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  Copyright (C) 2010-2018  CEA/DEN
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
import sys
import unittest

import src.product
from src.salomeTools import Sat

class TestCase(unittest.TestCase):
    """Test of the configure command"""

    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")

    def test_010(self):
        # Test the configure command with a product in cmake
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_build_dir = src.product.get_product_config(sat.cfg, product_name).build_dir
        expected_file_path = os.path.join(expected_build_dir, 'CMakeCache.txt')
       
        sat.configure(appli + ' --product ' + product_name)
        
        if os.path.exists(os.path.join(expected_build_dir, expected_file_path)):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the configure command with a product in autotools
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_CVS'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_build_dir = src.product.get_product_config(sat.cfg, product_name).build_dir
        expected_file_path = os.path.join(expected_build_dir, 'config.log')
       
        sat.configure(appli + ' --product ' + product_name)
        
        if os.path.exists(os.path.join(expected_build_dir, expected_file_path)):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_030(self):
        # Test the configure command with a product in script mode
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'Python'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_build_dir = src.product.get_product_config(sat.cfg, product_name).build_dir
      
        sat.configure(appli + ' --product ' + product_name)
        
        if os.path.exists(expected_build_dir):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_040(self):
        # Test the 'sat -h configure'
        OK = "KO"

        import configure
        
        if "The configure command executes in the build directory" in configure.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
