#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('LIBXML_DIR', prereq_dir)
    env.set('LIBXML2_ROOT_DIR', prereq_dir)
    root = env.get('LIBXML_DIR')
    pyver = 'python' + env.get('PYTHON_VERSION')
    
    env.prepend('INCLUDE', os.path.join(root, 'include'))
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('PATH', os.path.join(root, 'lib'))
    env.prepend('PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('LIBXML_DIR', '/usr')
    env.set('LIBXML2_ROOT_DIR', '/usr')
    pass
