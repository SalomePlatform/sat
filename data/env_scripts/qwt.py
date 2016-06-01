#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('QWTHOME', prereq_dir)
    env.set('QWT_ROOT_DIR', prereq_dir)
    root = env.get('QWTHOME')
    
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('QWTHOME', '/usr')
    env.set('QWT_ROOT_DIR', '/usr')
    pass
