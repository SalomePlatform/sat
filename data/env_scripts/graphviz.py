#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('GRAPHVIZROOT', prereq_dir)
    env.set('GRAPHVIZ_ROOT_DIR', prereq_dir)
    root = env.get('GRAPHVIZROOT')

    l = []
    l.append(os.path.join(root, 'bin'))
    l.append(os.path.join(root, 'include', 'graphviz'))
    env.prepend('PATH', l)

    l = []
    l.append(os.path.join(root, 'lib'))
    l.append(os.path.join(root, 'lib', 'graphviz'))
    
    if platform.system() == "Windows" :
        env.prepend('LIB', l)
        env.prepend('INCLUDE', os.path.join(root, 'include'))
    else :
        env.prepend('LD_LIBRARY_PATH', l)

def set_nativ_env(env):
    env.set('GRAPHVIZROOT', '/usr')
    env.set('GRAPHVIZ_ROOT_DIR', '/usr')
    pass
