#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('SETUPTOOLDIR', prereq_dir)
    env.set('SETUPTOOLS_ROOT_DIR', prereq_dir)   # update for cmake 
    
    env.prepend('PATH', os.path.join(prereq_dir, 'bin'))

    versionPython = env.get('PYTHON_VERSION')
    env.prepend('PYTHONPATH',os.path.join(prereq_dir, 'lib', 'python' + versionPython, 'site-packages'))
    env.prepend('PYTHONPATH', os.path.join(prereq_dir, 'bin'))

def set_nativ_env(env):
    env.set('SETUPTOOLS_ROOT_DIR', '/usr')   # update for cmake
    env.set('SETUPTOOLDIR', '/usr')
    pass
