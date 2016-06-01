#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('TCL_ROOT_DIR', prereq_dir) # update for cmake
    env.set('TCLHOME', prereq_dir)

    root = env.get('TCLHOME')
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    env.prepend('INCLUDE', os.path.join(root, 'include'))
    
    l = []
    l.append(os.path.join(root, 'lib'))
    l.append(os.path.join(root, 'lib', 'tcl'))
    #http://computer-programming-forum.com/57-tcl/1dfddc136afccb94.htm
    #Tcl treats the contents of that variable as a list. Be happy, for you can now use drive letters on windows.
    env.prepend('TCLLIBPATH', l, sep=" ")
    env.set('TCL_SHORT_VERSION', version[:version.rfind('.')])

def set_nativ_env(env):
    env.set('TCL_ROOT_DIR', '/usr') # update for cmake
    env.set('TCLHOME', '/usr')
