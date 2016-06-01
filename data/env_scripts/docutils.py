#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('DOCUTILSDIR', prereq_dir)
    env.set('DOCUTILS_ROOT_DIR', prereq_dir) # update for cmake
    pyver = 'python' + env.get('PYTHON_VERSION')
    env.prepend('PATH', os.path.join(env.get('DOCUTILSDIR'), 'bin'))
    env.prepend('PYTHONPATH', os.path.join(env.get('DOCUTILSDIR'), 'lib', pyver, 'site-packages'))

def set_nativ_env(env):
    env.set('DOCUTILS_ROOT_DIR', '/usr') # update for cmake
    env.set('DOCUTILSDIR', '/usr')
    pass
