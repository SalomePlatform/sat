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
import threading
import time
import unittest

from src.salomeTools import Sat
from unittestpy.tools import check_proc_existence_and_kill_multi

sleep_time = 2

class TestCase(unittest.TestCase):
    """sat config --edit"""
    
    def test_010(self):
        # Test the launch of the editor when invoking the config -e
        OK = "KO"

        sat = Sat("-oUSER.editor='cooledit'")
        sat.config()
        cmd_config = threading.Thread(target=sat.config, args=('-e',))
        cmd_config.start()

        time.sleep(sleep_time)

        editor = sat.cfg.USER.editor
        pid = check_proc_existence_and_kill_multi(editor + ".*" + "salomeTools\.pyconf", 10)

        if pid:
            OK = "OK"
        self.assertEqual(OK, "OK")

    def test_020(self):
        # Test the launch of the editor when invoking the config -e appli-test
        OK = "KO"

        sat = Sat("-oUSER.editor='cooledit'")
        sat.config()
        cmd_config = threading.Thread(target=sat.config, args=('appli-test -e',))
        cmd_config.start()

        time.sleep(sleep_time)

        editor = sat.cfg.USER.editor
        pid = check_proc_existence_and_kill_multi(editor + ".*" + "appli-test\.pyconf", 10)

        if pid:
            OK = "OK"
        self.assertEqual(OK, "OK")
 
# test launch
if __name__ == '__main__':
    unittest.main()
    pass
