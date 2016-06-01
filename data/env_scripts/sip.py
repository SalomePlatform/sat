#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('SIPDIR', prereq_dir)
    root = env.get('SIPDIR')

    # [CMake GUI] Nouveau nom pour SIPDIR = SIP_ROOT_DIR 22/03/2013
    env.set('SIP_ROOT_DIR', prereq_dir)
    
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.prepend('CPLUS_INCLUDE_PATH', os.path.join(root, 'include', pyver))

    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib', pyver, 'site-packages'))

    pyqt = env.get('PYQTDIR')
    env.set('PYQT_SIPS_DIR', pyqt)

def set_nativ_env(env):
    env.set('SIPDIR', '/usr')
    env.set('SIP_ROOT_DIR','/usr')
    pass
