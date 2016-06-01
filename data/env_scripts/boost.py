#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('BOOSTDIR', prereq_dir)
    env.set('BOOST_ROOT_DIR', prereq_dir)
    root = env.get('BOOSTDIR')
    
    env.prepend('PATH', os.path.join(root, 'include'))
    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'lib'))
    else :
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
        
def set_nativ_env(env):
    env.set('BOOSTDIR', '/usr')
    env.set('BOOST_ROOT_DIR', '/usr')
    pass
