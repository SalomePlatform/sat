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

import src.salomeTools as SAT
import src.debug as DBG # Easy print stderr (for DEBUG only)
import src.loggingSimple as LOG

class TestCase(unittest.TestCase):
  "Test the sat --help commands"""
  
  debug = False
  
  def tearDown(self):
    # print "tearDown", __file__
    # assure self.logger clear for next test
    logger = LOG.getUnittestLogger()
    logs = logger.getLogsAndClear()
    # using assertNotIn() is too much verbose
    self.assertFalse("ERROR" in logs)
    self.assertFalse("CRITICAL" in logs)
  
  def test_000(self):
    logger = LOG.getUnittestLogger()
    # one shot setUp() for this TestCase
    if self.debug: DBG.push_debug(True)
    SAT.setNotLocale() # test english

  def test_999(self):
    # one shot tearDown() for this TestCase
    SAT.setLocale() # end test english
    if self.debug: DBG.pop_debug()

  def test_010(self): # TODO fix logger unittest
    cmd = "sat --help"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    out = res.getValue()
    self.assertTrue(" - config" in out)
    self.assertTrue(" - prepare" in out)
    self.assertTrue(" - compile" in out)

  def test_011(self):
    logger = LOG.getUnittestLogger()
    cmd = "--help"
    s = SAT.Sat(logger)
    returnCode = s.execute_cli(cmd)
    self.assertTrue(returnCode.isOk())
    logs = logger.getLogs()
    DBG.write("test_011 logger", logs)
    self.assertTrue(" - config" in logs)
    self.assertTrue(" - prepare" in logs)
    self.assertTrue(" - compile" in logs)
    
  def test_030(self):
    cmd = "sat config --help"
    returnCode = SAT.launchSat(cmd)
    self.assertTrue(returnCode.isOk())
    out = returnCode.getValue()
    DBG.write("test_030 stdout", out)
    self.assertTrue("--value" in out)

  def test_031(self):
    logger = LOG.getUnittestLogger()
    cmd = "config --help"
    s = SAT.Sat(logger)
    returnCode = s.execute_cli(cmd)
    self.assertTrue(returnCode.isOk())
    logs = logger.getLogs()
    DBG.write("test_031 logger", logs)
    self.assertTrue("--help" in logs)

  def test_032(self):
    logger = LOG.getUnittestLogger()
    cmd = "prepare --help"
    s = SAT.Sat(logger)
    returnCode = s.execute_cli(cmd)
    self.assertTrue(returnCode.isOk())
    logs = logger.getLogs()
    DBG.write("test_031 logger", logs)
    self.assertTrue("--help" in logs)

  def test_040(self):
    logger = LOG.getUnittestLogger()
    cmd = "config --list"
    s = SAT.Sat(logger)
    returnCode = s.execute_cli(cmd)
    self.assertTrue(returnCode.isOk())
    logs = logger.getLogs()
    self.assertTrue("Applications" in logs)

  def test_050(self):
    cmds = SAT.getCommandsList()
    DBG.write("test_050 getCommandsList", cmds)
    for c in cmds:
      cmd = "sat %s --help" % c
      DBG.write("test_050", cmd)
      returnCode = SAT.launchSat(cmd)
      if not returnCode.isOk():
        DBG.write("test_050 %s" % cmd, returnCode.getValue(), True)
      self.assertTrue(returnCode.isOk())
      out = returnCode.getValue()
      DBG.write("test_050 %s stdout" % c, out)
      self.assertTrue("The %s command" % c in out)
      self.assertTrue("Available options" in out)
      
  def test_051(self):
    logger = LOG.getUnittestLogger()
    cmds = SAT.getCommandsList()
    for c in cmds:
      cmd = "%s --help" % c
      DBG.write("test_051", cmd)
      s = SAT.Sat(logger)
      returnCode = s.execute_cli(cmd)
      self.assertTrue(returnCode.isOk())
      logs = logger.getLogsAndClear()
      DBG.write(cmd, logs)
      self.assertTrue("The %s command" % c in logs)
      self.assertTrue("Available options" in logs)
                
if __name__ == '__main__':
    unittest.main(exit=False)
    pass
