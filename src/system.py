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


def git_extract(from_what, tag, where, logger, environment=None):
    '''Extracts sources from a git repository.
    
    :param from_what str: The remote git repository.
    :param tag str: The tag.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :param environment src.environment.Environ: The environment to source when
                                                extracting.
    :return: True if the extraction is successful
    :rtype: boolean
    '''
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
        command = command % {'remote': from_what, 
                             'tag': tag, 
                             'where': str(where), 
                             'where_git': where_git }

    logger.write(command + "\n", 5)

    logger.logTxtFile.write("\n" + command + "\n")
    logger.logTxtFile.flush()
    res = subprocess.call(command,
                          cwd=str(where.dir()),
                          env=environment.environ.environ,
                          shell=True,
                          stdout=logger.logTxtFile,
                          stderr=subprocess.STDOUT)
    return (res == 0)

def archive_extract(from_what, where, logger):
    '''Extracts sources from an archive.
    
    :param from_what str: The path to the archive.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :return: True if the extraction is successful
    :rtype: boolean
    '''
    try:
        archive = tarfile.open(from_what)
        for i in archive.getmembers():
            archive.extract(i, path=str(where))
        return True, os.path.commonprefix(archive.getnames())
    except Exception as exc:
        logger.write("archive_extract: %s\n" % exc)
        return False, None

def cvs_extract(protocol, user, server, base, tag, product, where,
                logger, checkout=False, environment=None):
    '''Extracts sources from a cvs repository.
    
    :param protocol str: The cvs protocol.
    :param user str: The user to be used.
    :param server str: The remote cvs server.
    :param base str: .
    :param tag str: The tag.
    :param product str: The product.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :param checkout boolean: If true use checkout cvs.
    :param environment src.environment.Environ: The environment to source when
                                                extracting.
    :return: True if the extraction is successful
    :rtype: boolean
    '''

    opttag = ''
    if tag is not None and len(tag) > 0:
        opttag = '-r ' + tag

    cmd = 'export'
    if checkout:
        cmd = 'checkout'
    elif len(opttag) == 0:
        opttag = '-DNOW'
    
    if len(protocol) > 0:
        root = "%s@%s:%s" % (user, server, base)
        command = "cvs -d :%(protocol)s:%(root)s %(command)s -d %(where)s %(tag)s %(product)s" % \
            { 'protocol': protocol, 'root': root, 'where': str(where.base()),
              'tag': opttag, 'product': product, 'command': cmd }
    else:
        command = "cvs -d %(root)s %(command)s -d %(where)s %(tag)s %(base)s/%(product)s" % \
            { 'root': server, 'base': base, 'where': str(where.base()),
              'tag': opttag, 'product': product, 'command': cmd }

    logger.write(command + "\n", 5)

    if not where.dir().exists():
        where.dir().make()

    logger.logTxtFile.write("\n" + command + "\n")
    logger.logTxtFile.flush()        
    res = subprocess.call(command,
                          cwd=str(where.dir()),
                          env=environment.environ.environ,
                          shell=True,
                          stdout=logger.logTxtFile,
                          stderr=subprocess.STDOUT)
    return (res == 0)

def svn_extract(user,
                from_what,
                tag,
                where,
                logger,
                checkout=False,
                environment=None):
    '''Extracts sources from a svn repository.
    
    :param user str: The user to be used.
    :param from_what str: The remote git repository.
    :param tag str: The tag.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :param checkout boolean: If true use checkout svn.
    :param environment src.environment.Environ: The environment to source when
                                                extracting.
    :return: True if the extraction is successful
    :rtype: boolean
    '''
    if not where.exists():
        where.make()

    if checkout:
        command = "svn checkout --username %(user)s %(remote)s %(where)s" % \
            { 'remote': from_what, 'user' : user, 'where': str(where) }
    else:
        command = ""
        if os.path.exists(str(where)):
            command = "/bin/rm -rf %(where)s && " % \
                { 'remote': from_what, 'where': str(where) }
        
        if tag == "master":
            command += "svn export --username %(user)s %(remote)s %(where)s" % \
                { 'remote': from_what, 'user' : user, 'where': str(where) }       
        else:
            command += "svn export -r %(tag)s --username %(user)s %(remote)s %(where)s" % \
                { 'tag' : tag, 'remote': from_what, 'user' : user, 'where': str(where) }
    
    logger.logTxtFile.write(command + "\n")
    
    logger.write(command + "\n", 5)
    logger.logTxtFile.write("\n" + command + "\n")
    logger.logTxtFile.flush()
    res = subprocess.call(command,
                          cwd=str(where.dir()),
                          env=environment.environ.environ,
                          shell=True,
                          stdout=logger.logTxtFile,
                          stderr=subprocess.STDOUT)
    return (res == 0)