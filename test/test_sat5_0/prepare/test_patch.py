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
import shutil
import unittest

from src.salomeTools import Sat
import src.product
from unittestpy.tools import outRedirection

class TestCase(unittest.TestCase):
    """Test of the patch command"""

    def test_010(self):
        # Test the patch command with a product in dev mode
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_DEV'

        sat = Sat("-oUSER.output_level=2")
               
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
       
        sat.patch(appli + ' --product ' + product_name)
        
        new_expected_text = 'HELLO WORLD MODIFIED\n'
        f = open(expected_file_path, 'r')
        text = f.readlines()[0]
        
        OK2 = 'KO'
        if text == new_expected_text:
            OK2 = 'OK'         

        if (OK1, OK2)==('OK', 'OK'):
            OK = 'OK'
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the patch command with a product with no sources found
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_DEV'

        sat = Sat('')
        sat.config(appli)
        
        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        
        if os.path.exists(expected_src_dir):
            shutil.rmtree(expected_src_dir)
               
        # output redirection
        my_out = outRedirection()
        
        sat.patch(appli + ' --product ' + product_name)
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()
        
        if "No sources found for the " + product_name +" product" in res:
            OK = 'OK'
        self.assertEqual(OK, 'OK')

    def test_030(self):
        # Test the patch command with a product without patch
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_ARCHIVE'

        sat = Sat('-v4')
                      
        sat.source(appli + ' --product ' + product_name)
               
        # output redirection
        my_out = outRedirection()
        
        sat.patch(appli + ' --product ' + product_name)
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()
        
        if "No patch for the " + product_name +" product" in res:
            OK = 'OK'
        self.assertEqual(OK, 'OK')

    def test_040(self):
        # Test the patch command with a product with a not valid patch
        OK = 'KO'

        appli = 'appli-test'
        product_name = 'PRODUCT_DEV'

        sat = Sat("-oPRODUCTS.PRODUCT_DEV.default.patches=['/']")
                      
        sat.source(appli + ' --product ' + product_name)
               
        # output redirection
        my_out = outRedirection()
        
        sat.patch(appli + ' --product ' + product_name)
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()
        
        if "Not a valid patch" in res:
            OK = 'OK'
        self.assertEqual(OK, 'OK')

    def test_050(self):
        # Test the sat -h patch
        OK = "KO"

        import patch
        
        if "The patch command apply the patches on the sources of" in patch.description():
            OK = "OK"
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
