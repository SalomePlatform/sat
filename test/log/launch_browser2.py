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
import threading
import time

# get execution path
testdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(testdir, '..', '..'))
sys.path.append(os.path.join(testdir, '..', '_testTools'))
sys.path.append(os.path.join(testdir, '..', '..','commands'))

from salomeTools import Sat
from tools import check_proc_existence_and_kill_multi
import HTMLTestRunner

sleep_time = 2

class TestLog(unittest.TestCase):
    '''Test of log command: launch of browser
    '''
    def test_launch_browser(self):
        '''Test the launch of browser when invoking the log command
        '''

        OK = "KO"

        sat = Sat("-oUSER.browser='konqueror'")
        time.sleep(sleep_time)
        cmd_log = threading.Thread(target=sat.log, args=('',))
        cmd_log.start()

        time.sleep(sleep_time)

        browser = sat.cfg.USER.browser
        pid = check_proc_existence_and_kill_multi(browser + ".*" + "hat\.xml", 10)

        if pid:
            OK = "OK"
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
