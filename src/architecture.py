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
In this file : all the stuff that can change with the architecture 
on which SAT is running
'''

import os, sys, platform

def is_windows():
    '''method that checks windows OS
      
    :rtype: boolean
    '''
    return platform.system() == 'Windows'

def get_user():
    '''method that gets the username that launched sat  
    
    :rtype: str
    '''
    try :
        if is_windows():
            # In windows case, the USERNAME environment variable has to be set
            user_name=os.environ['USERNAME']
        else: # linux
            import pwd
            user_name=pwd.getpwuid(os.getuid())[0]
    except :
        user_name="Unknown"
    return user_name

	
def get_distribution(codes):
    '''Gets the code for the distribution
    
    :param codes L{Mapping}: The map containing distribution correlation table.
    :return: The distribution on which salomeTools is running, regarding the 
             distribution correlation table contained in codes variable.
    :rtype: str
    '''
    if is_windows():
        return "W"

    # else get linux distribution description from platform, and encode it with code
    lin_distrib = platform.dist()[0].lower()
    distrib="not found"
    for dist in codes:
        if dist in lin_distrib:
            distrib = codes[dist]
            break
    if distrib=="not found":
        sys.stderr.write(_(u"Unknown distribution: '%s'\n") % distrib)
        sys.stderr.write(_(u"Please add your distribution to src/internal_config/distrib.pyconf\n"))
        sys.exit(-1)

    return distrib

def get_version_XY():
    """
    Return major and minor version of the distribution
    from a CentOS example, returns '7.6'
    extracted from platform.dist()
    """
    dist_version=platform.dist()[1].split('.')
    if len(dist_version)==1:
        version = dist_version[0]
    else:
        version = dist_version[0] + "." + dist_version[1]
    return version 


def get_distrib_version(distrib):
    '''Return the sat encoded version of the distribution
       This code is used in config to apend the name of the application directories
       withdistribution info"
    
    :param distrib str: The distribution on which the version will be found.
    :return: The version of the distribution on which salomeTools is running, 
             regarding the distribution correlation table contained in codes 
             variable.
    :rtype: str
    '''

    if is_windows():
        return platform.release()

    # get version from platform
    dist_version=platform.dist()[1].split('.')

    # encode it (conform to src/internal_config/distrib.pyconf VERSIONS dist
    if distrib == "CO":
        version=dist_version[0] # for centos, we only care for major version
    elif distrib == "UB":
        # for ubuntu, we care for major + minor version
        version=dist_version[0] + "." + dist_version[1] 
    elif distrib == "DB":
        if len(dist_version[0]) == 1:
            version="0"+dist_version[0]
        else:
            version=dist_version[0]  # unstable, and version >= 10
    elif distrib == "MG":
        version="0"+dist_version[0]
    else:
        version=dist_version[0]
        
    return version

def get_python_version():
    '''Gets the version of the running python.
    
    :return: the version of the running python.
    :rtype: str
    '''
    
    # The platform python module gives the answer
    return platform.python_version()

def get_nb_proc():
    '''Gets the number of processors of the machine 
       on which salomeTools is running.
    
    :return: the number of processors.
    :rtype: str
    '''
    
    try :
        import multiprocessing
        nb_proc=multiprocessing.cpu_count()
    except :
        nb_proc=int(os.sysconf('SC_NPROCESSORS_ONLN'))
    return nb_proc
