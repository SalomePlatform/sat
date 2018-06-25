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

from src.salomeTools import Sat
import src.product
from unittestpy.tools import outRedirection

class TestCase(unittest.TestCase):
    """Test of the clean command"""

    def test_010(self):
        # Test the clean command with no arguments (nothing to clean)
        OK = 'KO'

        appli = 'appli-test'

        sat = Sat()

        # output redirection
        my_out = outRedirection()
        
        sat.clean(appli)
        
        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()
        
        if "Nothing to suppress" in res:
            OK = 'OK'
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the clean of sources
        OK = "KO"

        appli = 'appli-test'
        product_name = "PRODUCT_GIT"

        sat = Sat()      
        
        # Make sure the sources exist
        sat.prepare(appli + " -p " + product_name)
        
        # Call the command
        sat.clean(appli + " -p " + product_name + " --sources", batch=True)
           
        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        
        if not os.path.exists(expected_src_dir):
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_030(self):
        # Test the clean of build
        OK = "KO"

        appli = 'appli-test'
        product_name = "PRODUCT_GIT"

        sat = Sat()      
        
        # Make sure the build exists
        sat.prepare(appli + " -p " + product_name)
        sat.configure(appli + " -p " + product_name)
        
        # Call the command
        sat.clean(appli + " -p " + product_name + " --build", batch=True)
           
        expected_build_dir = src.product.get_product_config(sat.cfg, product_name).build_dir
        
        if not os.path.exists(expected_build_dir):
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_040(self):
        # Test the clean of install
        OK = "KO"

        appli = 'appli-test'
        product_name = "PRODUCT_GIT"

        sat = Sat()      
        
        # Make sure the build exists
        sat.prepare(appli + " -p " + product_name)
        sat.configure(appli + " -p " + product_name)
        
        # Call the command
        sat.clean(appli + " -p " + product_name + " --install", batch=True)
           
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        
        if not os.path.exists(expected_install_dir):
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_050(self):
        # Test the clean of all (build, src, install)
        OK = "KO"

        appli = 'appli-test'
        product_name = "PRODUCT_GIT"

        sat = Sat()      
        
        # Make sure the build exists
        sat.prepare(appli + " -p " + product_name)
        sat.compile(appli + " -p " + product_name)
        
        # Call the command
        sat.clean(appli + " -p " + product_name + " --all", batch=True)
           
        expected_install_dir = src.product.get_product_config(sat.cfg, product_name).install_dir
        expected_build_dir = src.product.get_product_config(sat.cfg, product_name).build_dir
        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        
        if not os.path.exists(expected_install_dir) and not os.path.exists(expected_build_dir) and not os.path.exists(expected_src_dir):
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_060(self):
        # Test the clean with sources_without_dev option
        OK = "KO"

        appli = 'appli-test'
        product_name = "PRODUCT_GIT"
        product_name2 = "PRODUCT_DEV"

        sat = Sat()      
        
        # Make sure the build exists
        sat.prepare(appli + " -p " + product_name + "," + product_name2)
        
        # Call the command
        sat.clean(appli + " -p " + product_name + " --sources_without_dev", batch=True)
           
        expected_src_dir = src.product.get_product_config(sat.cfg, product_name).source_dir
        expected_src_dir2 = src.product.get_product_config(sat.cfg, product_name2).source_dir
        
        if not os.path.exists(expected_src_dir) and os.path.exists(expected_src_dir2):
            OK = "OK"
        self.assertEqual(OK, "OK")


    def test_070(self):
        # Test the sat -h clean
        OK = "KO"

        import clean
        
        if "The clean command suppress the source, build, or install" in clean.description():
            OK = "OK"
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
