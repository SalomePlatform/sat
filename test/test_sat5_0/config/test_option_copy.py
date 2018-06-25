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
    """sat config --copy"""
    
    def test_010(self):
        # Test the copy of a pyconf
        res = "KO"
        appli_to_copy = "appli-test"

        expected_file = os.path.expanduser(os.path.join('~','.salomeTools', 'Applications', 'LOCAL_' + appli_to_copy + '.pyconf'))
        if os.path.exists(expected_file):
            os.remove(expected_file)
               
        # The command to test
        sat = Sat('')
        sat.config('appli-test -c')

        if os.path.exists(expected_file):
            res = "OK"
            os.remove(expected_file)
        self.assertEqual(res, "OK")

# test launch
if __name__ == '__main__':
    unittest.main()
    pass
