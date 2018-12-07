#!/usr/bin/env python
#-*- coding:utf-8 -*-

# ToolBox for test framework

import os
import string
import subprocess


class SatTestError(Exception):
    """
    Exception class for test errors.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class SatNotApplicableError(Exception):
    """
    Exception class for test errors.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def ERROR(message):
    print("ERROR", message)
    raise SatTestError(message)
    
def NOT_APPLICABLE(message):
    print("NOT_APPLICABLE", message)
    raise SatNotApplicableError(message)

def compFloat(f1, f2, tol=10e-10):
    """Compares 2 numbers with tolerance tol."""
    diff = abs(f1 - f2)
    print("|f1-f2| = %s (tol=%s)" % (str(diff), str(tol)))
    if diff <= tol:
        comp = "OK"
    else:
        comp = "KO"
    return comp

def compFiles(f1, f2, tol=0):
    """Compares 2 files."""
    assert os.path.exists(f1), "compFiles: file not found: %s" % f1
    assert os.path.exists(f2), "compFiles: file not found: %s" % f2
    diffLine = os.popen("diff -y --suppress-common-lines %s %s" % (f1, f2))
    diff = len(string.split(diffLine.read(), "\n"))
    diffLine.close()
    print("nb of diff lines = %s (tol=%s)" % (str(diff), str(tol)))
    if diff <= tol:
        comp = "OK"
    else:
        comp = "KO"
    return comp

def mdump_med(med_file, dump_file, options):
    """Uses mdump to dump a med file."""
    assert isinstance(options, list), "Bad options for mdump: %s" % options
    assert len(options) == 3, "Bad options for mdump: %s" % options
    cmd = "mdump %s %s" % (med_file, " ".join(options))
    #print(cmd)

    with open(dump_file, "w") as df:
        pdump = subprocess.Popen(cmd, shell=True, stdout=df)
        st = pdump.wait()
    return st

def compMED(file1, file2, tol=0, diff_flags=""):
    """Compares 2 med files by using mdump."""

    # local utility method
    def do_dump(med):
        dump = os.path.join(os.environ['TT_TMP_RESULT'], os.path.basename(med) + ".mdump")
        st = mdump_med(med, dump, ["1", "NODALE", "FULL_INTERLACE"])
        if st != 0 or not os.path.exists(dump):
            raise Exception("Error mpdump %s" % med)

        # replace file name with "filename"
        with open(dump, "r") as ff:
            lines = ff.readlines()
        with open(dump, "w") as dumpfile:
            for line in lines:
                try:
                    line.index('Universal name of mesh')
                    continue
                except:
                    dumpfile.write(line.replace(med, 'filename'))
        return dump


    # begin method
    print(""">>>> compMED
 file1: %s
 file2: %s
""" % (file1, file2))

    if not os.path.exists(file1):
        print("compMED: file not found: '%s'" % file1)
        print("<<<< compMED\n")
        return 1
    if not os.path.exists(file2):
        print("compMED: file not found: '%s'" % file2)
        print("<<<< compMED\n")
        return 1

    dump1 = do_dump(file1)
    dump2 = do_dump(file2)

    diff_cmd = "diff %s %s %s" % (diff_flags, dump1, dump2)
    print(" >" + diff_cmd)
    pdiff = subprocess.Popen(diff_cmd, shell=True, stdout=subprocess.PIPE)
    status = pdiff.wait()
    print(" Diff =", status)
    if status != 0:
        print(pdiff.stdout.read())

    print("<<<< compMED\n")
    return status


class TOOLS_class(object):
    def __init__(self, base_ressources_dir, tmp_dir, test_ressources_dir):
        self.base_ressources_dir = base_ressources_dir
        self.tmp_dir = tmp_dir
        self.test_ressources_dir = test_ressources_dir
        pass

    def init(self):
        self.inFiles = []

    def ERROR(self, message):
        # Simulation d'un plantage
        ERROR(message)

    def compMED(self, file1, file2, tol=0):
        return compMED(file1, file2, tol, "--ignore-all-space")

    def compFloat(self, f1, f2, tol=10e-10):
        return compFloat(f1, f2, tol)

    def compFiles(self, f1, f2, tol=0):
        return compFiles(f1, f2, tol)

    def get_inFile(self, name=None):
        if not name:
            return self.base_ressources_dir
        self.inFiles.append(name)
        return os.path.join(self.base_ressources_dir, name)

    def get_outFile(self, name=None):
        if not name:
            return self.tmp_dir
        return os.path.join(self.tmp_dir, name)

    def writeInFiles(self, pylog):
        pylog.write('inFiles=%s\n' % str(self.inFiles))

