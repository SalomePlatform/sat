#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('DISTRIBUTE_ROOT_DIR', env.get('PYTHON_ROOT_DIR'))

    if platform.system() == "Windows" :
        env.prepend('PYTHONPATH',os.path.join(prereq_dir, 'lib', 'site-packages'))
    else:
        env.prepend('PATH', os.path.join(prereq_dir, 'bin'))
        pyver = 'python' + env.get('PYTHON_VERSION')
        env.prepend('PYTHONPATH', os.path.join(prereq_dir, 'lib', pyver, 'site-packages'))
        env.prepend('PYTHONPATH', os.path.join(prereq_dir, 'bin'))
    pass

def set_nativ_env(env):
    pass
