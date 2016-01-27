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
In this file : all the stuff that can change with the architecture on which SAT is running
'''

import os, sys, platform, pwd

def is_windows():
    '''method that checks windows OS  
    :rtype: boolean
    '''
    return platform.system() == 'Windows'

def get_user():
    '''method that gets the username that launched sat  
    :rtype: str
    '''
    # In windows case, the USERNAME environment variable has to be set
    if is_windows():
        if not os.environ.has_key('USERNAME'):
            raise Exception('USERNAME environment variable not set')
        return os.environ['USERNAME']
    else: # linux
        return pwd.getpwuid(os.getuid())[0]

def _lsb_release(args):
    '''Get system information with lsb_release.
    :param args str: The arguments to give to lsb_release.
    :return: The distribution.
    :rtype: str
    '''
    try:
        path = '/usr/local/bin:/usr/bin:/bin'
        lsb_path = os.getenv("LSB_PATH")
        if lsb_path is not None:
            path = lsb_path + ":" + path
        
        from subprocess import Popen, PIPE
        res = Popen(['lsb_release', args], env={'PATH': path}, stdout=PIPE).communicate()[0][:-1]
        # in case of python3, convert byte to str
        if isinstance(res, bytes):
            res = res.decode()
        return res
    except OSError:
        sys.stderr.write(_(u"lsb_release not installed\n"))
        sys.stderr.write(_(u"You can define $LSB_PATH to give the path to lsb_release\n"))
        sys.exit(-1)

def get_distribution(codes):
    '''Gets the code for the distribution
    :param codes L{Mapping}: The map containing distribution correlation table.
    :return: The distribution on which salomeTools is running, regarding the distribution correlation table contained in codes variable.
    :rtype: str
    '''
    if is_windows():
        return "Win"

    # Call to lsb_release
    distrib = _lsb_release('-si')
    if codes is not None and distrib in codes:
        distrib = codes[distrib]
    else:
        sys.stderr.write(_(u"Unknown distribution: '%s'\n") % distrib)
        sys.stderr.write(_(u"Please add your distribution to data/distrib.pyconf\n"))
        sys.exit(-1)

    return distrib


def get_distrib_version(distrib, codes):
    '''Gets the version of the distribution
    :param distrib str: The distribution on which the version will be found.
    :param codes L{Mapping}: The map containing distribution correlation table.
    :return: The version of the distribution on which salomeTools is running, regarding the distribution correlation table contained in codes variable.
    :rtype: str
    '''

    if is_windows():
        return platform.release()

    # Call to lsb_release
    version = _lsb_release('-sr')
    if distrib in codes:
        if version in codes[distrib]:
            version = codes[distrib][version]

    return version

def get_nb_bit():
    '''Gets the number of bytes.
    :return: the number of bytes of the OS on which salomeTools is running.
    :rtype: str
    '''

    # The platform python module gives the answer
    nb_bit = platform.architecture()[0]
    if nb_bit == "64bit":
        nb_bit = "64"
    elif nb_bit == "32bit":
        nb_bit = "32"
    else:
        sys.stderr.write(_(u"Unknown architecture: '%s'\n") % nb_bit)
        sys.exit(-1)

    return nb_bit

def get_python_version():
    '''Gets the version of the running python.
    :return: the version of the running python.
    :rtype: str
    '''
    
    # The platform python module gives the answer
    return platform.python_version()

def get_nb_proc():
    '''Gets the number of processors of the machine on which salomeTools is running.
    :return: the number of processors.
    :rtype: str
    '''
    
    try :
        import multiprocessing
        nb_proc=multiprocessing.cpu_count()
    except :
        nb_proc=int(os.sysconf('SC_NPROCESSORS_ONLN'))
    return nb_proc