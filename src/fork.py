#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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
import time
import pickle
import subprocess

# Display progress
# ----------------
def show_progress(logger, top, delai, ss=""):
    logger.write("\r%s\r%s %s / %s " % ((" " * 30), ss, top, (delai - top)), 4,
                 False)
    logger.flush()

def write_back(logger, message, level):
    logger.write("\r%s\r%s" % ((" " * 40), message), level)

# Launch command
# --------------
def launch_command(cmd, logger, cwd, args=[], log=None):
    if log:
        log = file(log, "a")
    logger.write("launch: %s\n" % cmd, 5, screenOnly=True)
    for arg in args:
        cmd += " " + arg
    prs = subprocess.Popen(cmd,
                           shell=True,
                           stdout=log,
                           stderr=subprocess.STDOUT,
                           cwd=cwd,
                           executable='/bin/bash')
    return prs

# Launch a batch
# --------------
def batch(cmd, logger, cwd, args=[], log=None, delai=20, sommeil=1):
    proc = launch_command(cmd, logger, cwd, args, log)
    top = 0
    sys.stdout.softspace = True
    begin = time.time()
    while proc.poll() is None:
        if time.time() - begin >= 1:
            show_progress(logger, top, delai, "batch:")
            if top == delai:
                logger.write("batch: time out KILL\n", 3)
                import signal
                os.kill(proc.pid, signal.SIGTERM)
                break
            else:
                begin = time.time()
                time.sleep(sommeil)
                top += 1
        sys.stdout.flush()
    else:
        write_back(logger, "batch: exit (%s)\n" % str(proc.returncode), 5)
    return (proc.returncode == 0), top

# Launch a salome process
# -----------------------
def batch_salome(cmd, logger, cwd, args, getTmpDir,
    pendant="SALOME_Session_Server", fin="killSalome.py",
    log=None, delai=20, sommeil=1, delaiapp=0):

    beginTime = time.time()
    launch_command(cmd, logger, cwd, args, log)

    if delaiapp == 0:
        delaiapp = delai

    # first launch salome (looking for .pidict file)
    top = 0
    found = False
    tmp_dir = getTmpDir()
    while (not found and top < delaiapp):
        if os.path.exists(tmp_dir):
            listFile = os.listdir(tmp_dir)
        else:
            listFile = []

        for file_name in listFile:
            if file_name.endswith("pidict"):
                # sometime we get a old file that will be removed by runSalome.
                # So we test that we can read it.
                currentTime = None
                try:
                    statinfo = os.stat(os.path.join(tmp_dir, file_name))
                    currentTime = statinfo.st_mtime
                except: pass

                if currentTime and currentTime > beginTime:
                    try:
                        file_ = open(os.path.join(tmp_dir, file_name), "r")
                        process_ids = pickle.load(file_)
                        file_.close()
                        for process_id in process_ids:
                            for __, cmd in process_id.items():
                                if cmd == [pendant]:
                                    found = True
                                    pidictFile = file_name
                    except:
                        file_.close()

        time.sleep(sommeil)
        top += 1
        show_progress(logger, top, delaiapp, "launching salome or appli:")

    # continue or not
    if found:
        write_back(logger, "batch_salome: started\n", 5)
    else:
        logger.write("batch_salome: FAILED to launch salome or appli\n", 3)
        return False, -1

    # salome launched run the script
    top = 0
    code = None
    while code is None:
        show_progress(logger, top, delai, "running salome or appli:")

        if not os.access(os.path.join(tmp_dir, pidictFile), os.F_OK):
            write_back(logger, "batch_salome: exit\n", 5)
            code = True
        elif top >= delai:
            # timeout kill the test
            os.system(fin)
            logger.write("batch_salome: time out KILL\n", 3)
            code = False
        else:
            # still waiting
            time.sleep(sommeil)
            top = top + 1

    return code, top
