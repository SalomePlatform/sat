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
            
def check_proc_existence(cmd, text_to_find):
    
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()