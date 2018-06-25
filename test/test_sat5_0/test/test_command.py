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

class TestTest(unittest.TestCase):
    """Test of the test command"""

    def test_010(self):
        # Test the test command
        OK = 'KO'
        tmp_file = "/tmp/test.txt"
        application = "SALOME-7.8.0"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        sat.test(application + " --grid GEOM --session light" )

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_testboard = [line.replace("\n", "") for line in log_files if 'testboard.xml' in line]
        
        text = open(log_testboard[0], "r").read()

        if '<session name="light">' in text:
            OK = 'OK'         
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the test command with PY type
        OK = 'KO'
        tmp_file = "/tmp/test.txt"
        application = "SALOME-7.8.0"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        sat.test(application + " --grid MED --session PY_test_withKernel" )

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_testboard = [line.replace("\n", "") for line in log_files if 'testboard.xml' in line]
        
        text = open(log_testboard[0], "r").read()

        if '<session name="PY_test_withKernel">' in text:
            OK = 'OK'         
        self.assertEqual(OK, 'OK')

    def test_030(self):
        # Test the sat -h test
        OK = "KO"

        import test
        
        if "The test command runs a test base on a SALOME installation" in test.description():
            OK = "OK"
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
