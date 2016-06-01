#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('PYQTDIR', prereq_dir)
    version_table = version.split('.') 
    if version_table[0] == '5':
        env.set('PYQT5_ROOT_DIR', prereq_dir)
    else:
        env.set('PYQT4_ROOT_DIR', prereq_dir)
    root = env.get('PYQTDIR')
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.set('PYQT_SIPS', os.path.join(root, 'sip'))
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', root)
    
    l = []
    l.append(root) # for old version of pyqt
    l.append(os.path.join(root, 'lib', pyver, 'site-packages'))
    env.prepend('PYTHONPATH', l)

def set_nativ_env(env):
    env.set('PYQTDIR', '/usr')
    env.set('PYQT4_ROOT_DIR', '/usr')
    pass
