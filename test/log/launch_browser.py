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
import shutil
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
        logDir = sat.cfg.SITE.log.log_dir
        logPath = os.path.join(logDir, sat.cfg.VARS.datehour + "_" + sat.cfg.VARS.command + ".xml")
        
        if os.path.exists(logPath):
            OK = "OK"
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal(self):
        '''Test the terminal option without application
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
        
        one = u"1"
        sys.stdin = io.StringIO(one)
        
        
        try:
            sat.log('-t')
            OK = "OK"
            sys.stdin = sys.__stdin__
        except:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal2(self):
        '''Test the terminal option with application
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
              
        sat.config('appli-test -v VARS.python')
        
        one = u"1"
        sys.stdin = io.StringIO(one)
        
        try:
            sat.log('appli-test -t --last')
            OK = "OK"
            sys.stdin = sys.__stdin__
        except:
            pass
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal3(self):
        '''Test the terminal option with 0 as input
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
              
        sat.config('appli-test -v VARS.python')
        
        zero = u"0\n1"
        sys.stdin = io.StringIO(zero)
        
        try:
            sat.log('--terminal')
            OK = "OK"
        finally:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal4(self):
        '''Test the terminal option with input bigger than the number of logs
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
              
        sat.config('appli-test -v VARS.python')
        
        nb_logs = len(os.listdir(sat.cfg.SITE.log.log_dir))
        
        nb_logs_u = unicode(str(nb_logs) + "\n1")
        sys.stdin = io.StringIO(nb_logs_u)
        
        try:
            sat.log('--terminal')
            OK = "OK"
        finally:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal5(self):
        '''Test the terminal option with input return
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
              
        sat.config('appli-test -v VARS.python')
        
        ret = unicode("\n0")
        sys.stdin = io.StringIO(ret)
        
        try:
            sat.log('--terminal')
            OK = "OK"
        finally:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal6(self):
        '''Test the terminal option with input not int
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
              
        sat.config('appli-test -v VARS.python')
        
        ret = unicode("blabla\n0")
        sys.stdin = io.StringIO(ret)
        
        try:
            sat.log('--terminal')
            OK = "OK"
        finally:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_terminal7(self):
        '''Test the terminal option and option last
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
        
        try:
            sat.log('--terminal --last')
            OK = "OK"
        finally:
            sys.stdin = sys.__stdin__
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_last(self):
        '''Test the option --last
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat("-oUSER.browser='konqueror'")
              
        sat.config('appli-test -v VARS.python')
        
        
        time.sleep(sleep_time)
        cmd_log = threading.Thread(target=sat.log, args=('appli-test --last',))
        cmd_log.start()
        
        time.sleep(sleep_time)

        browser = sat.cfg.USER.browser
        pid = check_proc_existence_and_kill(browser + ".*" + "xml")
        
        if pid:
            OK = "OK"
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_clean(self):
        '''Test the option --clean
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
               
        sat.config('-v VARS.user')
        
        nb_logs_t0 = len(os.listdir(sat.cfg.SITE.log.log_dir))

        sat.log('--clean 1')
        
        nb_logs_t1 = len(os.listdir(sat.cfg.SITE.log.log_dir))
        
        if nb_logs_t1-nb_logs_t0 == 0:
            OK = "OK"
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_clean2(self):
        '''Test the option --clean with big number of files to clean
        '''

        OK = "KO"
        
        # launch the command that will write a log
        sat = Sat()
               
        sat.config('-v VARS.user')
        
        nb_logs_t0 = len(os.listdir(sat.cfg.SITE.log.log_dir))
        
        if os.path.exists(sat.cfg.SITE.log.log_dir + "_save"):
            shutil.rmtree(sat.cfg.SITE.log.log_dir + "_save")
        shutil.copytree(sat.cfg.SITE.log.log_dir,sat.cfg.SITE.log.log_dir + "_save")
        
        sat.log('--clean ' + str(nb_logs_t0))
        
        nb_logs_t1 = len(os.listdir(sat.cfg.SITE.log.log_dir))
        
        shutil.rmtree(sat.cfg.SITE.log.log_dir)
        shutil.move(sat.cfg.SITE.log.log_dir + "_save", sat.cfg.SITE.log.log_dir)
                
        if nb_logs_t0-nb_logs_t1 > 10:
            OK = "OK"
        
        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_option_full(self):
        '''Test the option --full
        '''

        OK = "KO"

        sat = Sat("-oUSER.browser='konqueror'")
        time.sleep(sleep_time)
        cmd_log = threading.Thread(target=sat.log, args=('--full',))
        cmd_log.start()

        time.sleep(sleep_time)

        browser = sat.cfg.USER.browser
        check_proc_existence_and_kill(browser + ".*" + "xml")
        
        # Read and check the hat.xml file contains at least one log file corresponding to log
        hatFilePath = os.path.join(sat.cfg.SITE.log.log_dir, "hat.xml")
        xmlHatFile = src.xmlManager.ReadXmlFile(hatFilePath)
        for field in xmlHatFile.xmlroot:
            if field.attrib[b'cmd'] == b'log':
                OK = "OK"
                break

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_description(self):
        '''Test the sat -h log
        '''        

        OK = "KO"

        import log
        
        if "Gives access to the logs produced" in log.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
