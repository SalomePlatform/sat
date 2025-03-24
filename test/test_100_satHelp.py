#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import unittest
import initializeTest
import src
import src.salomeTools as SAT
import src.debug as DBG
import src.loggingSimple as LOG

class TestCase(unittest.TestCase):
  """Test the sat --help commands"""
  
  debug = False
  
  def tearDown(self):
    logger = LOG.getUnittestLogger()
    logs = logger.getLogsAndClear()
    self.assertFalse("ERROR" in logs)
    self.assertFalse("CRITICAL" in logs)
  
  def test_000(self):
    logger = LOG.getUnittestLogger()
    if self.debug: DBG.push_debug(True)
    SAT.setNotLocale()

  def test_999(self):
    SAT.setLocale()
    if self.debug: DBG.pop_debug()

  def test_010(self):
    cmd = "sat --help"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    out = res.getValue().decode('utf-8')
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
    out = returnCode.getValue().decode('utf-8')
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

  def test_050(self):
    cmds = SAT.getCommandsList()
    DBG.write("test_050 getCommandsList", cmds)
    for c in cmds:
      if c =="jobs": ## paramiko is required for jobs command
        continue 
      cmd = "sat %s --help" % c
      DBG.write("test_050", cmd)
      returnCode = SAT.launchSat(cmd)
      if not returnCode.isOk():
        DBG.write("test_050 %s" % cmd, returnCode.getValue(), True)
      self.assertTrue(returnCode.isOk())
      out = returnCode.getValue().decode('utf-8')
      DBG.write("test_050 %s stdout" % c, out)
      self.assertTrue("The %s command" % c in out)
      
  def test_051(self):
    logger = LOG.getUnittestLogger()
    cmds = SAT.getCommandsList()
    for c in cmds:
      if c =="jobs": ## paramiko is required for jobs command
        continue 
      cmd = "%s --help" % c
      DBG.write("test_051", cmd)
      s = SAT.Sat(logger)
      returnCode = s.execute_cli(cmd)
      self.assertTrue(returnCode.isOk())
      logs = logger.getLogsAndClear()
      DBG.write(cmd, logs)
                
if __name__ == '__main__':
    unittest.main(exit=False)
    pass
