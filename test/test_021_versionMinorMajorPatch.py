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

import unittest
import pprint as PP

import initializeTest # set PATH etc for test

import src.versionMinorMajorPatch as VMMP

verbose = False # True

class TestCase(unittest.TestCase):
  "Test the versionMajorMinorPatch.py"""

  def test_010(self):
    if verbose: print(PP.pformat(dir(self)))
    self.assertTrue(VMMP.only_numbers("") is None)
    self.assertEqual(VMMP.only_numbers("1.2.3"), "123")
    self.assertEqual(VMMP.only_numbers("\n11.12.13\n"), "111213")
    self.assertEqual(VMMP.only_numbers(" \n 11.\t\n\t..12.13-rc2\n"), "1112132")

  def test_015(self):
    res = "a_b_c"
    self.assertEqual(VMMP.remove_startswith("version_a_b_c", "version_".split()), res)
    self.assertEqual(VMMP.remove_startswith("v_a_b_c",       "version_ v_".split()), res)
    self.assertEqual(VMMP.remove_startswith("va_b_c",        "version_ v_ v".split()), res)

    ini = "version_a_b_c"
    self.assertEqual(VMMP.remove_startswith(ini, "V".split()), ini)
    self.assertEqual(VMMP.remove_startswith(ini, "_".split()), ini)
    self.assertEqual(VMMP.remove_startswith(ini, "a_b_c".split()), ini)
    self.assertEqual(VMMP.remove_startswith(ini, "VERSION".split()), ini)


  def test_020(self):
    res = [11, 222, 3333]
    self.assertEqual(VMMP.toList_majorMinorPatch("11.222.3333"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("11_222_3333"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("11.222_3333"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("  11.  222 . 3333  "), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("\n  11  .    222 .   3333   \n"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch(" \n11.\t222.\r3333\n "), res) # could be tricky

    self.assertEqual(VMMP.toList_majorMinorPatch("V11.222.3333"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("Version11_222_3333"), res)
    self.assertEqual(VMMP.toList_majorMinorPatch("Version_11_222_3333"), res)


    self.assertEqual(VMMP.toList_majorMinorPatch("11"), [11, 0, 0])
    self.assertEqual(VMMP.toList_majorMinorPatch("11.0"), [11, 0, 0])
    self.assertEqual(VMMP.toList_majorMinorPatch("11.2"), [11, 2, 0])
    self.assertEqual(VMMP.toList_majorMinorPatch("\n1 .    2  \n"), [1, 2, 0])

    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("11.")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("11.2.")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("11.2.3.")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch(".11")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("1_2_3_4")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch("_1_2_3_")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch(" \n 11...22.333-rc2\n")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch(" \n 11...22.333-rc2\n")
    with self.assertRaises(Exception): VMMP.toList_majorMinorPatch(" \n 11...22.333-rc2\n")


  def test_040(self):
    MMP = VMMP.MinorMajorPatch
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

    with self.assertRaises(Exception): MMP([-5, 2, 10])
    with self.assertRaises(Exception): MMP([5, -2, 10])
    with self.assertRaises(Exception): MMP([5, 2, -10])
    with self.assertRaises(Exception): MMP(['-123', 2, 10])

  def test_050(self):
    MMP = VMMP.MinorMajorPatch
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

    va = v101
    vb = v100
    self.assertFalse(va == vb)
    self.assertTrue(va >= vb)
    self.assertFalse(va <= vb)
    self.assertTrue(va != vb)
    self.assertTrue(va > vb)
    self.assertFalse(va < vb)

  def test_060(self):
    MMP = VMMP.MinorMajorPatch
    v0 = MMP("0")
    v1 = MMP("1")
    v2 = MMP("2")
    v123 = MMP("1.2.3")
    v456 = MMP("4.5.6")

    tests = """\
toto_from_1_to_2
   _from_1.0.0_to_2.0.0
_from_1_0.  0_to_  2.0_0
_from_V1.0.0_to_2.0.0
_from_version_1.0.0_to_2.0.0
version_1.0.0_to_2.0.0
VERSION_1.0.0_to_2.0.0""".split("\n")

    for a in tests:
      # print("test '%s'" % a)
      r1, r2 = VMMP.getRange_majorMinorPatch(a)
      self.assertEqual(r1, v1)
      self.assertEqual(r2, v2)

    a = "toto_to_2"
    r1, r2 = VMMP.getRange_majorMinorPatch(a)
    self.assertEqual(r1, v0)
    self.assertEqual(r2, v2)

    a = "toto_to_Version2"
    r1, r2 = VMMP.getRange_majorMinorPatch(a)
    self.assertEqual(r1, v0)
    self.assertEqual(r2, v2)

    a = "toto_from_1.2.3_to_Version4_5_6"
    r1, r2 = VMMP.getRange_majorMinorPatch(a)
    self.assertEqual(r1, v123)
    self.assertEqual(r2, v456)

    a = "toto_from_1.2.3_to_Version1_2_3"
    r1, r2 = VMMP.getRange_majorMinorPatch(a)
    self.assertEqual(r1, v123)
    self.assertEqual(r2, v123)

    # _from_ without _to_ does not matter
    tests = """\

toto
from
to
_from_
toto_from_2""".split("\n")

    for a in tests:
      rx = VMMP.getRange_majorMinorPatch(a, verbose=False)
      self.assertEqual(rx, None)

    # _to_ without _from_ does not matter, as implicit _from_ '0.0.0'
    # empty _to_ raise error
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("_to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("_from_to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("_from__to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("toto_from__to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("toto_from_123_to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("version_123_to_")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("version_to_")

    # min > max does matter
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("_from_3_to_2")
    with self.assertRaises(Exception): VMMP.getRange_majorMinorPatch("_from_3.2.5_to_V2_1_1")

if __name__ == '__main__':
  unittest.main(exit=False)
  pass
