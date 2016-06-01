#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('JINJADIR', prereq_dir)
    env.set('JINJA_ROOT_DIR', prereq_dir) # update for cmake   
    root = env.get('JINJADIR')
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib', pyver, 'site-packages'))
    env.prepend('PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages'))

def set_nativ_env(env):
    env.set('JINJA_ROOT_DIR', '/usr') # update for cmake
    env.set('JINJADIR', '/usr')
    pass
