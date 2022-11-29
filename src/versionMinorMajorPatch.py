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
class and utilities to define a version as MAJOR.MINOR.PATCH,
and range of versions

| Given a version number MAJOR.MINOR.PATCH separator "_" or "."
| increment the
| MAJOR version when you make incompatible API changes,
| MINOR version when you add functionality in a backwards-compatible manner,
| PATCH version when you make backwards-compatible bug fixes.
"""

import os
import sys

verbose = False # True

#############################################
def only_numbers(aStr):
  """
  Remove non numericals characters from string,

  :param aStr: string to work
  :return: None if no number presence
  """
  res = ''.join([nb for nb in aStr if nb in '0123456789'])
  if res == "":
    return None
  else:
    return res

#############################################
def remove_startswith(aStr, startsToCheck):
  """
  remove starting strings, if begining of aStr correspond
  order of list startsToCheck matter
  do the stuff only for the first correspondence in startsToCheck
  """
  for s in startsToCheck:
    if aStr.startswith(s):
      return aStr[len(s):]
  return aStr

#############################################
def toList_majorMinorPatch(aStr, verbose=False):
  """
  Returns list of integer as  [major, minor, patch] from a string,

  | accepts '1.2.3' '1_2_3' 'version_1.2.3' 'version1.2.3' 'v1.2.3',
  | completion '123' means '123.0.0', '1.2' means '1.2.0'
  | lower or upper
  | raise exception if problem
  """
  if verbose: print("toList_majorMinorPatch('%s')" % aStr)
  res = aStr.replace(" ", "")
  res = res.lower()
  res = remove_startswith(res, "version_ version v".split())
  res = res.replace(".", "_").split("_")
  if len(res) > 3:
    msg = "Not a major_minor_patch correct syntax: '%s'" % aStr
    raise Exception(msg)
  if len(res) == 0:
    msg = "An empty string is not a major_minor_patch syntax"
    raise Exception(msg)

  # complete MINOR.PATCH if not existing
  if len(res) == 1:
    res.append("0")
  if len(res) == 2:
    res.append("0")

  try:
    ii = int(res[0])
  except:
    msg = "major in major_minor_patch is not integer: '%s'" % aStr
    raise Exception(msg)
  if ii < 0:
    msg = "major in major_minor_patch is negative integer: '%s'" % aStr
    raise Exception(msg)

  try:
    ii = int(res[1])
  except:
    msg = "minor in major_minor_patch is not integer: '%s'" % aStr
    raise Exception(msg)
  if ii < 0:
    msg = "minor in major_minor_patch is negative integer: '%s'" % aStr
    raise Exception(msg)

  try:
    ii = int(res[2])
  except:
    msg = "patch in major_minor_patch is not integer: '%s'" % aStr
    raise Exception(msg)
  if ii < 0:
    msg = "patch in major_minor_patch is negative integer: '%s'" % aStr
    raise Exception(msg)

  return [int(i) for i in res]

#############################################
def toCompactStr_majorMinorPatch(version):
  """
  OBSOLETE method
  parameter version is list of integer as  [major, minor, patch]

  | returns "789" for [7, 8, 9]
  | warning:
  |   minor, pach have to be integer less than 10
  |   raise exception for [7, 10, 11]
  |   (which returns "71011" as ambigous 710.1.1 for example)
  """
  # forbidden use from nov. 2023 and SALOME 9.10.0
  raise Exception("obsolete toCompactStr_majorMinorPatch method: forbiden use of compact representation of '%s', fix problem in caller" % version)


#############################################
def getRange_majorMinorPatch(aStr, verbose=False):
  """
  extract from aStr a version range, defined as
  '*_from_aMinVersionTag_to_aMaxVersionTag' or
  '*version_aMinVersionTag_to_aMaxVersionTag'.

  where aMinVersionTag and aMaxVersionTag are compatible with MinorMajorPatch class syntaxes
  '1.2.3' or '1_2_3' etc.
  if not found '_from_' or 'version_' first then aMinVersionTag is '0.0.0'

  :param aStr: string to work
  :return: list [min, max], where min, max are MinorMajorPatch instances.
           else None if not found
  """
  tmp1 = aStr.lower().split("_to_")

  if len(tmp1) < 2:
    return None # no '_to_'
  if len(tmp1) > 2:
    msg = "more than one '_to_' is incorrect for version range: '%s'" % aStr
    raise Exception(msg)
  aMax = tmp1[1]

  # accept older syntax as 'version_1_0_0_to_2_0_0', (as '_from_1_0_0_to_2_0_0')
  if "version_" in tmp1[0] and "_from_" not in tmp1[0]:
    aStr_with_from = aStr.lower().replace("version_", "_from_", 1)
  else:
    aStr_with_from = aStr.lower()

  # print("aStr_with_from '%s' -> '%s'" % (aStr, aStr_with_from))

  tmp0 = aStr_with_from.split("_from_")
  tmp1 = aStr_with_from.split("_to_")

  if len(tmp0) > 2:
    msg = "more than one '_from_' is incorrect for version range: '%s'" % aStr
    raise Exception(msg)

  tmp2 = tmp1[0].split("_from_")

  if len(tmp2) == 2:
    aMin = tmp2[1]
  else:
    aMin ="0.0.0"

  if verbose:
    msg = "version min '%s' and version max '%s' in version range: '%s'" % (aMin, aMax, aStr)
    print(msg)

  try:
    rMin = MinorMajorPatch(aMin)
    rMax = MinorMajorPatch(aMax)
  except:
    msg = "problem version range in '%s'" % aStr
    raise Exception(msg)
    """if verbose:
      print("WARNING: problem version range in '%s'" % aStr)
    return None"""

  if rMin > rMax:
    msg = "version min '%s' > version max '%s' in version range: '%s'" % (rMin, rMax, aStr)
    raise Exception(msg)

  return [rMin, rMax]

#############################################
class MinorMajorPatch(object):
  """\
  class to define a version as MAJOR.MINOR.PATCH

  | Given a version number MAJOR.MINOR.PATCH separator "_" or "."
  | increment the
  | MAJOR version when you make incompatible API changes,
  | MINOR version when you add functionality in a backwards-compatible manner,
  | PATCH version when you make backwards-compatible bug fixes.
  """

  def __init__(self, version):
    if type(version) == list:
      aStr = '_'.join([str(i) for i in version])
      v = toList_majorMinorPatch(aStr)
    else:
      v = toList_majorMinorPatch(version)
    self.major = v[0]
    self.minor = v[1]
    self.patch = v[2]

  def __repr__(self, sep="_"):
    """example is 'version_1_2_3' """
    res = "version_%i%s%i%s%i" % (self.major, sep, self.minor, sep, self.patch)
    return res

  def __str__(self, sep="."):
    """example is '1.2.3' """
    res = "%i%s%i%s%i" % (self.major, sep, self.minor, sep, self.patch)
    return res

  def strSalome(self):
    """example is '1_2_3' """
    return self.__str__(sep="_")

  def strClassic(self):
    """example is '1.2.3' """
    return self.__str__(sep=".")

  def strCompact(self):
    """example is '123' from '1.2.3' """
    # forbidden use from nov. 2023 and SALOME 9.10.0
    raise Exception("obsolete strCompact method: forbiden use of compact representation of '%s', fix problem in caller" % str(self))
    # return toCompactStr_majorMinorPatch(self.toList())

  def toList(self):
    """example is list of integer [1, 2, 3] from '1.2.3' """
    return [self.major, self.minor, self.patch]

  def __lt__(self, other):
    res = (self.toList() < other.toList())
    return res

  def __le__(self, other):
    res = (self.toList() <= other.toList())
    return res

  def __gt__(self, other):
    res = (self.toList() > other.toList())
    return res

  def __ge__(self, other):
    res = (self.toList() >= other.toList())
    return res

  def __eq__(self, other):
    res = (self.toList() == other.toList())
    return res

  def __ne__(self, other):
    res = (self.toList() != other.toList())
    return res
