#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('OPENCV_ROOT_DIR', prereq_dir)
    env.set('OPENCV_HOME', prereq_dir)
    root = env.get('OPENCV_ROOT_DIR')
    
    env.prepend('PATH', os.path.join(root, 'include'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('OPENCV_ROOT_DIR', '/usr')
    env.set('OPENCV_HOME', '/usr')

