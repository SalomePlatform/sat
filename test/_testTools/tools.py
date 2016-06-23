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

import tempfile
import sys
import subprocess
import time

class outRedirection():
    '''redirection of standart output
    useful for testing the terminal display
    '''
    def __init__(self):
        '''initialization
        '''
        self._fstream = tempfile.NamedTemporaryFile(mode='w')
        self.saveout = sys.stdout
        sys.stdout = self._fstream

    def flush(self):
        self._fstream.flush()                

    def end_redirection(self):
        self._fstream.seek(0)
        ff = open(self._fstream.name, 'r')
        self.res = ff.read()
        self._fstream.close()
        sys.stdout = self.saveout
        
    def read_results(self):
        try:
            return self.res
        except Exception as exc:
            print('Problem with redirection : %s' % exc)
            sys.exit(1)

def kill9(pid):
    subprocess.call("kill -9 " + pid, shell=True)

def check_proc_existence_and_kill(regex):
    cmd = 'ps aux | grep "' + regex + '"'
    psRes = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
    psRes = psRes.split('\n')
    for line in psRes:
        if 'grep' in line or len(line) == 0:
            continue
        line2 = [i for i in line.split(' ') if i != '']
        pid = line2[1]
        kill9(pid)
        return pid
    return 0

def check_proc_existence_and_kill_multi(regex, nb_kills, time_between_two_checks = 1):
    found = False
    i = 0
    while not found and i < nb_kills :
        found = check_proc_existence_and_kill(regex)
        if found:
            return found
        time.sleep(time_between_two_checks)
        i+=1
    return 0