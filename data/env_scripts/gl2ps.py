#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('GL2PSDIR', prereq_dir)
    env.set('GL2PS_ROOT_DIR', prereq_dir)
    
    root = env.get('GL2PSDIR')
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('GL2PSDIR', '/usr')
    env.set('GL2PS_ROOT_DIR', '/usr')
    pass
