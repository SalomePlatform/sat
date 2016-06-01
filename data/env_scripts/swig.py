#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('SWIG_ROOT', prereq_dir)
    env.set('SWIG_ROOT_DIR', prereq_dir)
    
    if platform.system() == "Windows" :
        env.set('SWIG_LIB', os.path.join( prereq_dir, "lib" ) )
    else :
        env.set('SWIG_LIB', os.path.join( prereq_dir, "share", "swig", version) )

    root = env.get('SWIG_ROOT')
    env.prepend('PATH', os.path.join(root, 'bin'))

def set_nativ_env(env):
    env.set('SWIG_ROOT_DIR', '/usr')
    env.set('SWIG_ROOT', '/usr')
