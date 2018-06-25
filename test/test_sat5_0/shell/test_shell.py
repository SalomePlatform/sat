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

class TestCase(unittest.TestCase):
    """Test of the shell command"""

    def test_010(self):
        # Test the shell command with the --command option
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        sat.config()
        sat_way = sat.cfg.VARS.salometoolsway
        
        # Execute the shell command
        sat.shell("--command ls " + sat_way)

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_files = [line.replace("\n", "") for line in log_files]
        
        text = open(log_files[2], "r").read()

        if "salomeTools.py" in text:
            OK = 'OK'         
        self.assertEqual(OK, 'OK')

    def test_020(self):
        # Test the shell command with the --command option with a failing command
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        sat.config()
        
        # Execute the shell command
        res = sat.shell("--command i_fail")

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_files = [line.replace("\n", "") for line in log_files]
        
        text = open(log_files[2], "r").read()

        if "i_fail" in text and res == 1:
            OK = 'OK'         
        self.assertEqual(OK, 'OK')

    def test_030(self):
        # Test the sat -h shell
        OK = "KO"

        import shell
        
        if "Executes the shell command passed as argument" in shell.description():
            OK = "OK"
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
