#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path, platform

def set_env(env,prereq_dir,version,forBuild=None):
    version = '.'.join(version.replace('-', '.').split('.')[:2])
    env.set('FFTW_VERSION', version)

    env.set('FFTWHOME', prereq_dir)

    env.set('FFTW_ROOT_DIR', prereq_dir)
    root = env.get('FFTW_ROOT_DIR')

    env.prepend('PATH', root)
    env.prepend('PATH', os.path.join(root, 'bin'))

    l = []
    l.append(os.path.join(root, 'lib'))
    
    if platform.system() == "Windows" :
        env.prepend('PATH', l)
    else:
        env.prepend('LD_LIBRARY_PATH', l)

    env.set('FFTW_INCLUDE', os.path.join(root, 'include'))
    env.prepend('FFTWPATH', os.path.join(root, 'lib'))

def set_nativ_env(env):
    import sys
    pass


