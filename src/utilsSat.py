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

"""
utilities for sat
general useful simple methods
all-in-one import srs.utilsSat as UTS

| Usage:
| >> import srsc.utilsSat as UTS
| >> UTS.Popen('ls && etc...', ...)
"""

import os
import shutil
import errno
import stat
import time

import re
import tempfile
import subprocess as SP

import src.returnCode as RCO
import src.debug as DBG # Easy print stderr (for DEBUG only)


##############################################################################
# subprocess utilities, with logger functionnalities (trace etc.)
##############################################################################
    
def Popen(command, shell=True, cwd=None, env=None, stdout=SP.PIPE, stderr=SP.PIPE, logger=None):
  """
  make subprocess.Popen(cmd), with 
  call logger.trace and logger.error if problem as returncode != 0 
  """
  if True: #try:  
    proc = SP.Popen(command, shell=shell, cwd=cwd, env=env, stdout=stdout, stderr=SP.STDOUT)
    res_out, res_err = proc.communicate() # res_err = None as stderr=SP.STDOUT
    rc = proc.returncode
    
    DBG.write("Popen logger returncode", (rc, res_out))
    
    if rc == 0:
      if logger is not None:
        logger.trace("<OK> launch command rc=%s cwd=%s:\n%s" % (rc, cwd, command))
        logger.trace("<OK> result command stdout&stderr:\n%s" % res_out)
      return RCO.ReturnCode("OK", "Popen command done", value=res_out)
    else:
      if logger is not None:
        logger.warning("<KO> launch command rc=%s cwd=%s:\n%s" % (rc, cwd, command))
        logger.warning("<KO> result command stdout&stderr:\n%s" % res_out)
      return RCO.ReturnCode("KO", "Popen command problem", value=res_out)
  else: #except Exception as e:
    logger.error("<KO> launch command cwd=%s:\n%s" % (cwd, command))
    logger.error("launch command exception:\n%s" % e)
    return RCO.ReturnCode("KO", "Popen command problem")


def sleep(sec):
    time.sleep(sec)
