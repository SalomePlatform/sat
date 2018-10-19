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
class and utilities to define a version as MAJOR.MINOR.PATCH

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
  returns None if no numbers
  """
  res = ''.join([nb for nb in aStr if nb in '0123456789'])
  if res == "":
    return None
  else:
    return res

#############################################
def toList_majorMinorPatch(aStr):
  """
  Returns list of integer as  [major, minor, patch] from a string,
  raise exception if problem
  """
  if verbose: print("toList_majorMinorPatch('%s')" % aStr)
  res = aStr.replace(" ", "").replace(".", "_").split("_")
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
  parameter version is list of integer as  [major, minor, patch]

  | returns "789" for [7, 8, 9]
  | warning:
  |   minor, pach have to be integer less than 10
  |   raise exception for [7, 10, 11]
  |   (which returns "71011" as ambigous 710.1.1 for example)
  """
  if len(version) != 3:
    msg = "version major_minor_patch is incorrect: '%s'" % version
    raise Exception(msg)

  aStr = '_'.join([str(i) for i in version])
  toList_majorMinorPatch(aStr) # will raise error if problem (as too much or negative values)

  res = "".join([str(i) for i in version])
  if version[1] > 9 or version[2] > 9:
     raise Exception("ambigous major_minor_patch compact representation '%s' from '%s'" % (res, version))

  return res


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
    return toCompactStr_majorMinorPatch(self.toList())

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

#############################################
import unittest
import pprint as PP


class TestCase(unittest.TestCase):
  "Test the versionMajorMinorPatch.py"""

  def test_010(self):
    if verbose: print(PP.pformat(dir(self)))
    self.assertTrue(only_numbers("") is None)
    self.assertEqual(only_numbers("1.2.3"), "123")
    self.assertEqual(only_numbers("\n11.12.13\n"), "111213")
    self.assertEqual(only_numbers(" \n 11.\t\n\t..12.13-rc2\n"), "1112132")

  def test_020(self):
    res = [11, 222, 3333]
    self.assertEqual(toList_majorMinorPatch("11.222.3333"), res)
    self.assertEqual(toList_majorMinorPatch("11_222_3333"), res)
    self.assertEqual(toList_majorMinorPatch("11.222_3333"), res)
    self.assertEqual(toList_majorMinorPatch("  11.  222 . 3333  "), res)
    self.assertEqual(toList_majorMinorPatch("\n  11  .    222 .   3333   \n"), res)
    self.assertEqual(toList_majorMinorPatch(" \n11.\t222.\r3333\n "), res) # could be tricky

    self.assertEqual(toList_majorMinorPatch("11"), [11, 0, 0])
    self.assertEqual(toList_majorMinorPatch("11.0"), [11, 0, 0])
    self.assertEqual(toList_majorMinorPatch("11.2"), [11, 2, 0])
    self.assertEqual(toList_majorMinorPatch("\n1 .    2  \n"), [1, 2, 0])

    with self.assertRaises(Exception): toList_majorMinorPatch("")
    with self.assertRaises(Exception): toList_majorMinorPatch("11.")
    with self.assertRaises(Exception): toList_majorMinorPatch("11.2.")
    with self.assertRaises(Exception): toList_majorMinorPatch("11.2.3.")
    with self.assertRaises(Exception): toList_majorMinorPatch(".11")
    with self.assertRaises(Exception): toList_majorMinorPatch("1_2_3_4")
    with self.assertRaises(Exception): toList_majorMinorPatch("_1_2_3_")
    with self.assertRaises(Exception): toList_majorMinorPatch(" \n 11...22.333-rc2\n")
    with self.assertRaises(Exception): toList_majorMinorPatch(" \n 11...22.333-rc2\n")
    with self.assertRaises(Exception): toList_majorMinorPatch(" \n 11...22.333-rc2\n")


  def test_030(self):
    self.assertEqual(toCompactStr_majorMinorPatch([1, 2, 3]), "123")
    self.assertEqual(toCompactStr_majorMinorPatch([11, 2, 3]), "1123")
    self.assertEqual(toCompactStr_majorMinorPatch([1, 9, 9]), "199")

    with self.assertRaises(Exception): toCompactStr_majorMinorPatch([1, 2, 10])
    with self.assertRaises(Exception): toCompactStr_majorMinorPatch([1, 10, 3])
    with self.assertRaises(Exception): toCompactStr_majorMinorPatch([10, 10, 10])

  def test_040(self):
    MMP = MinorMajorPatch
    v = [1, 2, 3]
    self.assertEqual(MMP(v).__str__(), "1.2.3")
    self.assertEqual(MMP(v).__str__(sep="_"), "1_2_3")
    self.assertEqual(str(MMP(v)), "1.2.3")

    self.assertEqual(MMP(v).__repr__(), "version_1_2_3")
    self.assertEqual(MMP(v).__repr__(sep="."), "version_1.2.3")

    self.assertEqual(MMP(v).strSalome(), "1_2_3")
    self.assertEqual(MMP(v).strClassic(), "1.2.3")

    self.assertEqual(MMP(['  123 \n', 2, 10]).strClassic(), "123.2.10")
    self.assertEqual(MMP(['  123 \n', 2, 10]).strSalome(), "123_2_10")
    self.assertEqual(MMP(['  123 \n', 2, 9]).strCompact(), "12329") # no ambigous

    with self.assertRaises(Exception): MMP([-5, 2, 10])
    with self.assertRaises(Exception): MMP([5, -2, 10])
    with self.assertRaises(Exception): MMP([5, 2, -10])
    with self.assertRaises(Exception): MMP(['-123', 2, 10])
    with self.assertRaises(Exception): MMP([123, 2, 10].strCompact()) # ambigous

  def test_040(self):
    MMP = MinorMajorPatch
    v000 = MMP("0.0.0")
    v010 = MMP("0.1.0")
    v100 = MMP("1.0.0")
    v101 = MMP("1.0.1")

    va = v000
    vb = MMP("0.0.0")
    self.assertTrue(va == vb)
    self.assertTrue(va >= vb)
    self.assertTrue(va <= vb)
    self.assertFalse(va != vb)
    self.assertFalse(va > vb)
    self.assertFalse(va < vb)

    va = v000
    vb = v010
    self.assertFalse(va == vb)
    self.assertFalse(va >= vb)
    self.assertTrue(va <= vb)
    self.assertTrue(va != vb)
    self.assertFalse(va > vb)
    self.assertTrue(va < vb)


if __name__ == '__main__':
  unittest.main(exit=False)
  pass

