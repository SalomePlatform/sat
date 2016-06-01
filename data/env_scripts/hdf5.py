#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path, platform

def set_env(env, prereq_dir, version):
    env.set('HDF5HOME', prereq_dir)
    env.set('HDF5_DIR', prereq_dir)
    env.set('HDF5_ROOT', prereq_dir)
    env.set('HDF5_ROOT_DIR', prereq_dir) 
    root = env.get('HDF5HOME')
    
    env.prepend('PATH', os.path.join(root, 'bin'))

    env.set('HDF5_LIBRARIES', os.path.join(root, 'lib'))
    env.set('HDF5_INCLUDE_DIRS', os.path.join(root, 'include'))
    env.set('HDF5_VERSION', version)

    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'lib'))
    else :
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    
def set_nativ_env(env):
    env.set('HDF5HOME', '/usr')
    env.set('HDF5_ROOT', '/usr')
    env.set('HDF5_ROOT_DIR', '/usr')    # update for cmake    
    pass
