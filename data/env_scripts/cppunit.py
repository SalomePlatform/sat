#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('CPPUNITHOME', prereq_dir)
    env.set('CPPUNIT_ROOT', prereq_dir)
    env.set('CPPUNIT_ROOT_DIR', prereq_dir) # update for cmake   
    root = env.get('CPPUNITHOME')
    
    env.set('CPPUNITINSTDIR', root)
    env.prepend('PATH', os.path.join(root, 'bin'))
    import platform
    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'lib'))
    else :
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('CPPUNIT_ROOT_DIR', '/usr') # update for cmake 
    env.set('CPPUNITHOME','/usr')
    env.set('CPPUNIT_ROOT','/usr')
