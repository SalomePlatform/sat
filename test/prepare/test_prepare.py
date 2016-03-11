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
import io

# get execution path
testdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(testdir, '..', '..'))
sys.path.append(os.path.join(testdir, '..', '_testTools'))
sys.path.append(os.path.join(testdir, '..', '..','commands'))

from salomeTools import Sat
from tools import check_proc_existence_and_kill
from tools import outRedirection
import HTMLTestRunner
import src.xmlManager

sleep_time = 3

class TestLog(unittest.TestCase):
    '''Test of the prepare command
    '''
    
    def test_prepare_all(self):
        '''Test the prepare command with many ways to prepare
        '''
       
        OK = "KO"

        sat = Sat()

        try:
            sat.prepare('appli-test')
            OK = "OK"
        except:
            pass
        

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")
        

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
