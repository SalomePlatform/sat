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
import logging as LOGI

import initializeTest # set PATH etc for test

import src.salomeTools as SAT
import src.debug as DBG # Easy print stderr (for DEBUG only)
import src.loggingSimple as LOG

class TestCase(unittest.TestCase):
  "Test the compute_dependencies option of sat"
  
  debug = False
  
  def tearDown(self):
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

  def test_010(self):
    # Test compute_dependency help
    cmd = "sat compute_dependencies --help"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    out = res.getValue().decode('utf-8')
    self.assertTrue("compute_dependencies" in out)
    self.assertTrue("--products" in out)

  def test_020(self):
    # Test compute_dependency on APPLI_TEST
    cmd = "sat compute_dependencies APPLI_TEST --products KERNEL"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    logs = res.getValue().decode('utf-8')
    DBG.write("test_020 logger", logs)
    # Check that dependencies are listed
    self.assertTrue("Required products and dependencies:" in logs)
    self.assertTrue("Mandatory:" in logs)
    self.assertTrue("Optional:" in logs)

  def test_030(self):
    # Test compute_dependency with invalid application
    cmd = "sat compute_dependencies INVALID_APP --products KERNEL"
    res = SAT.launchSat(cmd)
    self.assertFalse(res.isOk())
    logs = res.getValue().decode('utf-8')
    self.assertTrue("CRITICAL" in logs)
    
  def test_040(self):
    # Test compute_dependency with multiple products
    cmd = "sat compute_dependencies APPLI_TEST --products KERNEL,GUI"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    logs = res.getValue().decode('utf-8')
    DBG.write("test_040 logger", logs)
    # Check that dependencies are listed
    self.assertTrue("Required products and dependencies:" in logs)
    self.assertTrue("Mandatory:" in logs)
    self.assertTrue("Optional:" in logs)

  def test_050(self):
    # Test compute_dependency without products option
    cmd = "sat compute_dependencies APPLI_TEST"
    res = SAT.launchSat(cmd)
    self.assertFalse(res.isOk())
    logs = res.getValue().decode('utf-8')
    self.assertTrue("ERROR" in logs)
    self.assertTrue("The --products option is required" in logs)

  def test_060(self):
    # Test compute_dependency with invalid products
    cmd = "sat compute_dependencies APPLI_TEST --products INVALID_PRODUCT"
    res = SAT.launchSat(cmd)
    self.assertTrue(res.isOk())
    logs = res.getValue().decode('utf-8')
    self.assertTrue("Total unique dependencies: 0" in logs)



if __name__ == '__main__':
    unittest.main(exit=False)
    pass
