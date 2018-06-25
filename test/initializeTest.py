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


"""\
initialize PATH etc... for salomeTools unittest test files
"""

"""
https://docs.python.org/2/library/os.html
os.environ mapping is captured the first time the os module is imported, 
typically during Python startup as part of processing site.py. 
Changes to the environment made after this time are not reflected 
in os.environ, except for changes made by modifying os.environ directly.

On some platforms, including FreeBSD and Mac OS X, 
setting environ may cause memory leaks.
"""

import os
import sys
import pprint as PP

# get path to salomeTools sources directory parent
satdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# sys.stderr.write("INFO    : initializeTest needs '%s' in sys.path:\n%s\n" % (satdir, PP.pformat(sys.path)))

if satdir not in sys.path:
  # get path to salomeTools sources FIRST as prepend
  # Make the src & commands package accessible from all test code
  sys.path.insert(0, satdir)
  sys.stderr.write("""\
WARNING : sys.path not set for salomeTools, fixed for you:
          sys.path prepend '%s'
          sys.path:\n%s\n""" % (satdir, PP.pformat(sys.path)))
  # os.environ PATH is not set...
  # supposedly useful only for subprocess launch from sat
  # see https://docs.python.org/2/library/os.html
  # On some platforms, including FreeBSD and Mac OS X, 
  # setting environ may cause memory leaks.
  # sys.stderr.write("os.environ PATH:\n%s\n" % PP.pformat(os.environ["PATH"].split(":")))
  sys.stderr.write("INFO    : to fix this message type:\n  'export PYTHONPATH=%s:${PYTHONPATH}'\n" % satdir)
  

