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
import src
from tools import outRedirection
from tools import check_proc_existence_and_kill
import HTMLTestRunner

sleep_time = 3

class TestConfig(unittest.TestCase):
    '''OPTION EDIT.
    '''
    
    def test_edit_userconfig(self):
        '''Test the launch of the editor when invoking the config -e
        '''

        OK = "KO"

        sat = Sat("-oUSER.editor='cooledit'")
        cmd_config = threading.Thread(target=sat.config, args=('-e',))
        cmd_config.start()

        time.sleep(sleep_time)

        editor = sat.cfg.USER.editor
        pid = check_proc_existence_and_kill(editor + ".*" + "salomeTools\.pyconf")

        if pid:
            OK = "OK"
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_edit_appli(self):
        '''Test the launch of the editor when invoking the config -e appli-test
        '''

        OK = "KO"

        sat = Sat("-oUSER.editor='cooledit'")
        cmd_config = threading.Thread(target=sat.config, args=('appli-test -e',))
        cmd_config.start()

        time.sleep(sleep_time)

        editor = sat.cfg.USER.editor
        pid = check_proc_existence_and_kill(editor + ".*" + "appli-test\.pyconf")

        if pid:
            OK = "OK"
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")
 
# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
