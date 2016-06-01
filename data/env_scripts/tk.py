#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('TK_ROOT_DIR', prereq_dir)   # update for cmake 
    env.set('TKHOME', prereq_dir)
    root = env.get('TKHOME')
    
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    
    l = []
    l.append(os.path.join(root, 'lib'))
    l.append(os.path.join(root, 'lib', 'tk'))
    #http://computer-programming-forum.com/57-tcl/1dfddc136afccb94.htm
    #Tcl treats the contents of that variable as a list. Be happy, for you can now use drive letters on windows.
    env.prepend('TKLIBPATH', l, sep=" ")

def set_nativ_env(env):
    env.set('TK_ROOT_DIR', '/usr')   # update for cmake
    env.set('TKHOME', '/usr')
