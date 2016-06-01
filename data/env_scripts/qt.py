#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('QTDIR', prereq_dir)
    version_table = version.split('.') 
    if version_table[0] == '5':
        env.set('QT5_ROOT_DIR', prereq_dir)
    else:
        env.set('QT4_ROOT_DIR', prereq_dir)

    root = env.get('QTDIR')
    
    env.prepend('PATH', os.path.join(root, 'bin'))

    if version_table[0] == '5':
        env.set('QT_PLUGIN_PATH', os.path.join(prereq_dir, 'plugins'))
        env.set('QT_QPA_PLATFORM_PLUGIN_PATH', os.path.join(prereq_dir, 'plugins'))

    if platform.system() == "Windows" :
        env.prepend('LIB', os.path.join(root, 'lib'))
        env.prepend('PATH', os.path.join(root, 'lib'))
    else :
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    env.set('QTDIR','/usr')
    env.set('QT4_ROOT_DIR','/usr')
    pass


