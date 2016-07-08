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
from tools import outRedirection
import HTMLTestRunner

class TestJobs(unittest.TestCase):
    '''Test of the jobs command
    '''

    def test_jobs(self):
        '''Test the jobs command
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the jobs command
        sat.jobs("--name .test --publish" )

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_jobs = [line.replace("\n", "") for line in log_files if 'jobs.xml' in line]
        
        text = open(log_jobs[0], "r").read()
        
        expected_res = [
        "Establishing connection with all the machines",
        "Executing the jobs",
        "Results for job"
        ]
        
        res = 0
        for exp_res in expected_res:
            if exp_res not in text:
                res += 1
        
        if res == 0:
            OK = 'OK'
                         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_jobs_only_jobs(self):
        '''Test the jobs command with option --only_jobs
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the jobs command
        sat.jobs("--name .test --publish --only_jobs Job 1" )

        ff = open(tmp_file, "r")
        log_files = ff.readlines()
        ff.close()
        os.remove(tmp_file)
        log_jobs = [line.replace("\n", "") for line in log_files if 'jobs.xml' in line]
        
        text = open(log_jobs[0], "r").read()
        
        expected_res = [
        "Establishing connection with all the machines",
        "Executing the jobs",
        "Results for job"
        ]
        
        res = 0
        for exp_res in expected_res:
            if exp_res not in text:
                res += 1
        
        if res == 0:
            OK = 'OK'
                         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_no_option_name(self):
        '''Test the jobs command without --name option
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.jobs()

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')
        
    def test_file_conf_not_found(self):
        '''Test the jobs command with a wrong file configuration
        '''
        OK = 'KO'
        tmp_file = "/tmp/test.txt"

        sat = Sat("-l " + tmp_file)
        
        # Execute the job command
        res = sat.jobs("--name NOTEXIST" )

        if res == 1:
            OK = 'OK'         
        # pyunit method to compare 2 str
        self.assertEqual(OK, 'OK')

    def test_option_list(self):
        '''Test the display of the right value of "sat jobs --list"
        '''
        
        OK = "KO"

        # output redirection
        my_out = outRedirection()

        # The command to test
        sat = Sat()
        sat.jobs('--list')

        # stop output redirection
        my_out.end_redirection()

        # get results
        res = my_out.read_results()

        # get results
        if "ERROR" not in res:
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

    def test_description(self):
        '''Test the sat -h jobs
        '''        

        OK = "KO"

        import jobs
        
        if "The jobs command launches maintenances that are described in the dedicated jobs configuration file." in jobs.description():
            OK = "OK"

        # pyunit method to compare 2 str
        self.assertEqual(OK, "OK")

# test launch
if __name__ == '__main__':
    HTMLTestRunner.main()
