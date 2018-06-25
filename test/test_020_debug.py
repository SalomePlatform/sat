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
import unittest

import initializeTest # set PATH etc for test

import src.debug as DBG # Easy print stderr (for DEBUG only)
import src.pyconf as PYF # 0.3.7

_EXAMPLES = {
1 : """\
  messages:
  [
    {
      stream : "sys.stderr" # modified
      message: 111 # modified
      name: 'Harry'
    }
    {
      stream : $messages[0].stream
      message: 1.23e4 # modified do not work 0.3.7
      name: 'Ruud'
    }
    {
      stream : "HELLO " + $messages[0].stream
      message: 'Bienvenue'
      name: "Yves"
    }
  ]
""",

2 : """\
  aa: 111
  bb: $aa + 222
""",

3 : """\
  aa: Yves
  bb: "Herve" # avoid Hervé -> 'utf8' codec can't decode byte
""",

4 : """\
  aa: Yves
  bb: "Hervé" # avoid Hervé -> 'utf8' codec can't decode byte
""",


}


class TestCase(unittest.TestCase):
  "Test the debug.py"""
  
  def test_000(self):
    # one shot setUp() for this TestCase
    # DBG.push_debug(True)
    # SAT.setNotLocale() # test english
    return
    
  def test_005(self):
    res = DBG.getLocalEnv()
    self.assertTrue(len(res.split()) > 0)
    self.assertTrue("USER :" in res)
    self.assertTrue("LANG :" in res)
       
  def test_010(self):
    inStream = DBG.InStream(_EXAMPLES[1])
    self.assertEqual(inStream.getvalue(), _EXAMPLES[1])
    cfg = PYF.Config(inStream)
    self.assertEqual(len(cfg.messages), 3)
    outStream = DBG.OutStream()
    DBG.saveConfigStd(cfg, outStream)
    res = outStream.value
    DBG.write("test_010 cfg std", res)
    self.assertTrue("messages :" in res)
    self.assertTrue("'sys.stderr'" in res)
    
  def test_020(self):
    inStream = DBG.InStream(_EXAMPLES[2])
    cfg = PYF.Config(inStream)
    res = DBG.getStrConfigDbg(cfg)
    DBG.write("test_020 cfg dbg", res)
    ress = res.split("\n")
    self.assertTrue(".aa" in ress[0])
    self.assertTrue(": '111'" in ress[0])
    self.assertTrue(".bb" in ress[1])
    self.assertTrue(": $aa + 222 " in ress[1])
    self.assertTrue("--> '333'" in ress[1])
    
  def test_025(self):
    inStream = DBG.InStream(_EXAMPLES[1])
    cfg = PYF.Config(inStream)
    outStream = DBG.OutStream()
    DBG.saveConfigDbg(cfg, outStream)
    res = outStream.value
    DBG.write("test_025 cfg dbg", res)
    for i in range(len(cfg.messages)):
      self.assertTrue("messages[%i].name" % i in res)
    self.assertTrue("--> 'HELLO sys.stderr'" in res)

      
  def test_999(self):
    # one shot tearDown() for this TestCase
    # SAT.setLocale() # end test english
    # DBG.pop_debug()
    return
    
if __name__ == '__main__':
    unittest.main(exit=False)
    pass

