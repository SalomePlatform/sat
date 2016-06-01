#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('DOXYGENDIR', prereq_dir)
    env.set('DOXYGEN_ROOT_DIR', prereq_dir)
    env.prepend('PATH', os.path.join(env.get('DOXYGENDIR'), 'bin'))

def set_nativ_env(env):
    env.set('DOXYGENDIR', '/usr')
    env.set('DOXYGEN_ROOT_DIR', '/usr')
    pass
