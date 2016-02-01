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
sys.path.append(os.path.join(testdir, '..', '..', '..', 'src'))
sys.path.append(os.path.join(testdir, '..', '..', '..', 'test', '__TOOLS__'))

from salomeTools import salomeTools
from tools import outRedirection

class TestConfig(unittest.TestCase):
    '''pyunit class : each method execute one test.
    '''
    
    def test_option_value(self):
        '''Test the display of the right value of "sat config -v VARS.hostname"
        '''
        # expected value
        expected = '\x1b[36mhostname\x1b[0m: is221560\n'

        # output redirection
        my_out = outRedirection()

        # The command to test
        sat = salomeTools('')
        sat.config('-v VARS.hostname')

        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()

        # pyunit method to compare 2 str
        self.assertEqual(res, expected)

# test launch
if __name__ == '__main__':
    unittest.main()