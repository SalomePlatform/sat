#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('NETGENHOME', prereq_dir)
    
    env.set('NETGEN_ROOT_DIR', prereq_dir)
    root = env.get('NETGENHOME')
    
    env.set('NETGEN_INCLUDE_DIRS', os.path.join(root, 'include'))
    env.set('NETGEN_LIBRARIES', os.path.join(root, 'lib'))
    env.prepend('PATH', os.path.join(root, 'bin'))
    
    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'lib'))
    else :
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('NETGEN_ROOT_DIR', '/usr')    # update for cmake
    env.set('NETGENHOME', '/usr')
    pass
