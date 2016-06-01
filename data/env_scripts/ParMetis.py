#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('PARMETISDIR', prereq_dir)
    env.set('PARMETIS_ROOT_DIR', prereq_dir)   # update for cmake 
    root = env.get('PARMETISDIR')

    env.prepend('LD_LIBRARY_PATH', root)
    env.prepend('PATH', root)
#    env.prepend('PATH', os.path.join(root, "Graphs"))

def set_nativ_env(env):
    pass
