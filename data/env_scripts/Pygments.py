#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('PYGMENTS_ROOT_DIR', prereq_dir) # update for cmake
    env.set('PYGMENTSDIR', prereq_dir)
    root = env.get('PYGMENTSDIR')
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages'))

def set_nativ_env(env):
    pass
