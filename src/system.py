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

'''
In this file : all functions that do a system call, 
like open a browser or an editor, or call a git command
'''

import subprocess
import os
import tarfile

from . import printcolors

def show_in_editor(editor, filePath, logger):
    '''open filePath using editor.
    
    :param editor str: The editor to use.
    :param filePath str: The path to the file to open.
    '''
    # default editor is vi
    if editor is None or len(editor) == 0:
        editor = 'vi'
    
    if '%s' not in editor:
        editor += ' %s'

    try:
        # launch cmd using subprocess.Popen
        cmd = editor % filePath
        logger.write('Launched command:\n' + cmd + '\n', 5)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
    except:
        logger.write(printcolors.printcError(_("Unable to edit file %s\n") 
                                             % filePath), 1)

##
# Extracts sources from a git repository.
def git_extract(from_what, tag, where, logger):
    if not where.exists():
        where.make()
    if tag == "master" or tag == "HEAD":
        command = "git clone %(remote)s %(where)s" % \
                    { 'remote': from_what, 'tag': tag, 'where': str(where) }
    else:
        # NOTICE: this command only works with recent version of git
        #         because --work-tree does not work with an absolute path
        where_git = os.path.join( str(where), ".git" )
        command = "rmdir %(where)s && git clone %(remote)s %(where)s && " + \
                  "git --git-dir=%(where_git)s --work-tree=%(where)s checkout %(tag)s"
        command = command % { 'remote': from_what, 'tag': tag, 'where': str(where), 'where_git': where_git }

    logger.write(command + "\n", 5)

    res = subprocess.call(command, cwd=str(where.dir()), shell=True,
                          stdout=logger.logTxtFile, stderr=subprocess.STDOUT)
    return (res == 0)

def archive_extract(from_what, where, logger):
    try:
        archive = tarfile.open(from_what)
        for i in archive.getmembers():
            archive.extract(i, path=str(where))
        return True, os.path.commonprefix(archive.getnames())
    except Exception as exc:
        logger.write("archive_extract: %s\n" % exc)
        return False, None