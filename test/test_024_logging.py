#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import unittest
import pprint as PP
import logging as LOGI
from logging.handlers import BufferingHandler
import src
import src.debug as DBG

verbose = False

_TRACE = LOGI.INFO - 2 # just below info

class LoggerSat(LOGI.Logger):
  """
  Elementary prototype for logger sat
  add a level TRACE as log.trace(msg) 
  below log.info(msg)
  above log.debug(msg)
  to assume store long log asci in files txt under/outside files xml
  """
  
  def __init__(self, name, level=LOGI.INFO):
    """
    Initialize the logger with a name and an optional level.
    """
    super(LoggerSat, self).__init__(name, level)
    LOGI.addLevelName(_TRACE, "TRACE")
    # LOGI.TRACE = _TRACE # only for coherency,
    
  def trace(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity '_TRACE'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.trace("Houston, we have a %s", "long trace to follow")
    """
    if self.isEnabledFor(_TRACE):
        self._log(_TRACE, msg, args, **kwargs)

class TestCase(unittest.TestCase):
  """Test the debug.py"""
  
  initialLoggerClass = [] # to keep clean module logging
  
  def test_000(self):
    # one shot setUp() for this TestCase
    self.initialLoggerClass.append(LOGI._loggerClass)
    LOGI.setLoggerClass(LoggerSat)
    if verbose:
      DBG.push_debug(True)
    pass
  
  def test_999(self):
    # one shot tearDown() for this TestCase
    if verbose:
      DBG.pop_debug()
    LOGI.setLoggerClass(self.initialLoggerClass[0])
    return
  
  def test_010(self):
    # LOGI.setLoggerClass(LoggerSat) # done once in test_000
    name = "testLogging"
    lgr = LOGI.getLogger(name) # create it
    lgr.setLevel("DEBUG")
    self.assertEqual(lgr.__class__, LoggerSat)
    self.assertEqual(lgr.name, name)
    self.assertIn("trace", dir(lgr))
    if sys.version_info.major == 3 and sys.version_info.minor > 10:
      self.assertIn("TRACE", LOGI.getLevelNamesMapping().keys())
      self.assertIn(_TRACE, LOGI.getLevelNamesMapping().values())
    self.assertEqual(LOGI.getLevelName(LOGI.INFO), "INFO")
    self.assertEqual(LOGI.getLevelName(_TRACE), "TRACE")
    
    # creation d'un handler pour chaque log sur la console
    formatter = LOGI.Formatter('%(levelname)-8s :: %(message)s')
    # stream_handler = LOGI.handlers.StreamHandler() # log outputs in console
    stream_handler = LOGI.handlers.BufferingHandler(1000) # log outputs in memory
    stream_handler.setLevel(LOGI.DEBUG)
    stream_handler.setFormatter(formatter)
    lgr.addHandler(stream_handler)
    lgr.warning("!!! test warning")
    lgr.info("!!! test info")
    lgr.trace("!!! test trace")
    lgr.debug("!!! test debug")
    self.assertEqual(len(stream_handler.buffer), 4)
    rec = stream_handler.buffer[-1]
    self.assertEqual(rec.levelname, "DEBUG")
    self.assertEqual(rec.msg, "!!! test debug")
    self.assertEqual(stream_handler.get_name(), None) # what to serve ?
    
  def test_020(self):
    name = "testLogging"
    lgr = LOGI.getLogger(name) #  find it as created yet in test_010
    stream_handler = lgr.handlers[0]
    rec = stream_handler.buffer[-1]
    self.assertEqual(rec.levelname, "DEBUG")
    self.assertEqual(rec.msg, "!!! test debug")
    
if __name__ == '__main__':
    unittest.main(exit=False)
    pass

