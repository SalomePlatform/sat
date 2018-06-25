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

class TestCase(unittest.TestCase):
    """Test create file .pyconf"""
    
    def test_010(self):
        # Test creation of ~/.salomeTools/salomeTools.pyconf
        print "stupidity HAVE TO NOT touch user ~/.salomeTools"
        return
        
        res = "KO"
        user_dir = os.path.expanduser(os.path.join('~','.salomeTools'))
        user_dir_save = os.path.expanduser(os.path.join('~','.salomeTools_save'))
        if os.path.exists(user_dir_save):
            shutil.rmtree(user_dir_save)
        if os.path.exists(user_dir):
            shutil.move(user_dir, user_dir_save)
               
        # The command to test
        sat = Sat('')
        sat.config('-v .')

        expected_file = os.path.expanduser(os.path.join('~','.salomeTools', 'salomeTools.pyconf'))

        if os.path.exists(expected_file):
            res = "OK"

        shutil.rmtree(user_dir)
        shutil.move(user_dir_save, user_dir)
        self.assertEqual(res, "OK")

    def test_020(self):
        # Test override VARS
        OK = "KO"
        
        # The command to test
        sat = Sat("-oVARS.user='user_test'")
        sat.config()

        if sat.cfg.VARS.user == 'user_test':
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_030(self):
        # Test override INTERNAL
        OK = "KO"
        
        # The command to test
        sat = Sat("-oINTERNAL.sat_version='V0'")
        sat.config()

        if sat.cfg.INTERNAL.sat_version == 'V0':
            OK = "OK"
        self.assertEqual(OK, "OK")

    """
    def test_040(self):
        # Test override SITE
        OK = "KO"
        
        # The command to test
        sat = Sat("-oSITE.jobs.config_path='/tmp'")
        sat.config()

        if sat.cfg.SITE.jobs.config_path == '/tmp':
            OK = "OK"

        self.assertEqual(OK, "OK")
    """

    def test_050(self):
        # Test override APPLICATION
        OK = "KO"
        
        # The command to test
        sat = Sat("-oAPPLICATION.out_dir='/tmp'")
        sat.config('appli-test')

        if sat.cfg.APPLICATION.out_dir == '/tmp':
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_060(self):
        # Test override PRODUCTS
        OK = "KO"
        
        # The command to test
        sat = Sat("-oPRODUCTS.PRODUCT_GIT.default.name='test'")
        sat.config('')

        if sat.cfg.PRODUCTS.PRODUCT_GIT.default.name == 'test':
            OK = "OK"
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
