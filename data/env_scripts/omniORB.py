#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('OMNIORB_ROOT_DIR', prereq_dir) # update for cmake    
    root = env.get('OMNIORB_ROOT_DIR')
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH',os.path.join(root, 'lib'))
    
    env.prepend( 'PYTHONPATH', os.path.join(root, 'lib') )
    env.prepend( 'PYTHONPATH', os.path.join(root, 'lib', 'python') )
    env.prepend( 'PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages') )
    env.prepend( 'PYTHONPATH', os.path.join(root, 'lib64', pyver, 'site-packages') )

    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'bin', 'x86_win32'))
        env.prepend('LD_LIBRARY_PATH',os.path.join(root, 'lib', 'x86_win32'))
        env.prepend( 'PYTHONPATH', os.path.join(root, 'lib', 'x86_win32') )

def set_nativ_env(env):
    env.set('OMNIORB_ROOT_DIR', "/usr") # update for cmake
    env.set('OMNIORBDIR', "/usr")
    env.set('OMNIORB_DIR', "/usr")
    env.set('OMNIORBDIR_INC', "/usr/include/omniORB4")
    pass
