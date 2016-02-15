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

from salomeTools import Sat
from tools import check_proc_existence_and_kill
import HTMLTestRunner

class TestLog(unittest.TestCase):
    '''Test of log command: launch of browser
    '''
    
    def test_launch_browser(self):
        '''Test the launch of browser when invoking the log command
        '''

        OK = "KO"

        sat = Sat("-oUSER.browser='konqueror'")
        cmd_log = threading.Thread(target=sat.log, args=('',))
        cmd_log.start()

        time.sleep(2)

        browser = sat.cfg.USER.browser
        pid = check_proc_existence_and_kill(browser + ".*" + "xml")

        if pid:
            OK = "OK"
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")
        
    def test_write_xmllog(self):
        '''Test the write of xml log when invoking a command
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
        sat.config('appli-test -v USER.browser')
        
        # get log file path
        logDir = sat.cfg.SITE.log.logDir
        logPath = os.path.join(logDir, sat.cfg.VARS.datehour + "_" + sat.cfg.VARS.command + ".xml")
        
        if os.path.exists(logPath):
            OK = "OK"
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal(self):
        '''Test the write of xml log when invoking a command
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
        
        # overwrite the raw_input function in order to be able to test
        new_ask_value = lambda x: 1
        sys.modules['log'].ask_value = new_ask_value
        
        try:
            sat.log('-t')
            OK = "OK"
        except:
            pass
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal2(self):
        '''Test the write of xml log when invoking a command
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
        
        # overwrite the raw_input function in order to be able to test
        new_ask_value = lambda x: 1
        sys.modules['log'].ask_value = new_ask_value
        
        sat.config('appli-test -v VARS.python')
        
        try:
            sat.log('appli-test -t')
            OK = "OK"
        except:
            pass
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
