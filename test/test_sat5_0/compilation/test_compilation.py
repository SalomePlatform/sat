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
    """Test of the compile command"""

    def test_010(self):
        # Test the compile command with '--products' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')

        sat.clean(appli + ' --build --install --product ' + product_name, batch=True)
        sat.compile(appli + ' --product ' + product_name)
        
        if os.path.exists(expected_file_path):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the configure command with '--fathers' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'
        product_name2 = 'PRODUCT_ARCHIVE'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name +"," +product_name2)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')
        expected_install_dir2 = src.product.get_product_config(sat.cfg, product_name2).install_dir
        expected_file_path2 = os.path.join(expected_install_dir2, 'bin/hello-archive')
        
        sat.clean(appli + ' --build --install --product ' + product_name +"," +product_name2, batch=True)
        sat.compile(appli + ' --with_fathers --product ' + product_name)
        
        if os.path.exists(expected_file_path) and os.path.exists(expected_file_path2):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')
        
    def test_030(self):
        # Test the configure command with '--children' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'
        product_name2 = 'PRODUCT_ARCHIVE'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name +"," +product_name2)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')
        expected_install_dir2 = src.product.get_product_config(sat.cfg, product_name2).install_dir
        expected_file_path2 = os.path.join(expected_install_dir2, 'bin/hello-archive')

        sat.clean(appli + ' --build --install --product ' + product_name +"," +product_name2, batch=True)
        sat.compile(appli + ' --with_children --product ' + product_name2)
        
        if os.path.exists(expected_file_path) and os.path.exists(expected_file_path2):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_040(self):
        # Test the configure command with '--clean_all' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'
        product_name2 = 'PRODUCT_ARCHIVE'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name +"," +product_name2)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')
        expected_install_dir2 = src.product.get_product_config(sat.cfg, product_name2).install_dir
        expected_file_path2 = os.path.join(expected_install_dir2, 'bin/hello-archive')

        sat.compile(appli + ' --with_children --product ' + product_name2)
        
        sat.compile(appli + ' --clean_all --with_children --product ' + product_name2, batch=True)
        
        if os.path.exists(expected_file_path) and os.path.exists(expected_file_path2):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_050(self):
        # Test the configure command with '--clean_install' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'
        product_name2 = 'PRODUCT_ARCHIVE'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name +"," +product_name2)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')
        expected_install_dir2 = src.product.get_product_config(sat.cfg, product_name2).install_dir
        expected_file_path2 = os.path.join(expected_install_dir2, 'bin/hello-archive')

        sat.compile(appli + ' --with_children --product ' + product_name2)
        
        sat.compile(appli + ' --clean_install --with_children --product ' + product_name2, batch=True)
        
        if os.path.exists(expected_file_path) and os.path.exists(expected_file_path2):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_060(self):
        # Test the configure command with '--make_flags' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')

        sat.clean(appli + ' --build --install --product ' + product_name, batch=True)
        sat.compile(appli + ' --make_flags 3 --product ' + product_name)
               
        if os.path.exists(expected_file_path):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_070(self):
        # Test the configure command with '--show' option
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_GIT'

        sat = Sat()
                            
        sat.prepare(appli + ' --product ' + product_name)
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_file_path = os.path.join(expected_install_dir, 'bin/hello')

        sat.clean(appli + ' --build --install --product ' + product_name, batch=True)
        sat.compile(appli + ' --show --product ' + product_name)
               
        if not(os.path.exists(expected_file_path)):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_080(self):
        # Test the configure command with '--stop_first_fail' option
        OK = 'KO'

        appli = 'appli-test'

        sat = Sat()
                            
        sat.prepare(appli + ' --product PRODUCT_CVS,Python')
        expected_install_dir = src.product.get_product_config(sat.cfg, "PRODUCT_CVS").install_dir

        sat.clean(appli + ' --build --install --product PRODUCT_CVS', batch=True)
        sat.compile(appli + ' --stop_first_fail --product PRODUCT_CVS,Python')
               
        if not(os.path.exists(expected_install_dir)):
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_090(self):
        # Test the 'sat -h compile' command to get description       

        OK = "KO"

        import compile
        
        if "The compile command constructs the products" in compile.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass

