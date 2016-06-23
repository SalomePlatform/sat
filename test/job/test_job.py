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
sys.path.append(os.path.join(testdir, '..', '..'))
sys.path.append(os.path.join(testdir, '..', '_testTools'))
sys.path.append(os.path.join(testdir, '..', '..','commands'))

from salomeTools import Sat
import HTMLTestRunner

class TestJob(unittest.TestCase):
    '''Test of the job command
    '''

    def test_job(self):
        '''Test the job command
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        sat.job("--jobs_config .test --job Job 1" )

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_config = [line.replace("\n", "") for line in log_files if 'config.xml' in line]
        
        text = open(log_config[0], "r").read()

        if "nb_proc" in text:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')


    def test_failing_job(self):
        '''Test the job command with a failing command
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.job("--jobs_config .test --job Job 4" )

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_file_conf_not_found(self):
        '''Test the job command with a wrong file configuration
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.job("--jobs_config NOTEXIST --job Job 4" )

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_no_option_jobs_config(self):
        '''Test the job command without --jobs_config option
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.job("--job Job 4" )

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_job_not_found(self):
        '''Test the job command without --jobs_config option
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.job("--jobs_config .test --job NOTEXIST" )

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_description(self):
        '''Test the sat -h job
        '''        

        OK = "KO"

        import job
        
        if "Executes the commands of the job defined in the jobs configuration file" in job.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
