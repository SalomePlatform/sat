#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    pyver = 'python' + env.get('PYTHON_VERSION')
    env.prepend('PYTHONPATH', os.path.join(prereq_dir, 'bin'))
    env.prepend('PYTHONPATH', os.path.join(prereq_dir, 'lib', pyver, 'site-packages'))
    #l0=os.path.join(prereq_dir, 'lib', pyver, 'site-packages','numpy')
    #l=[os.path.join(l0,'core'),os.path.join(l0,'fft'),os.path.join(l0,'lib'),os.path.join(l0,'linalg'),os.path.join(l0,'numarray'),os.path.join(l0,'random')]
    #env.prepend('LD_LIBRARY_PATH', os.path.join(prereq_dir, 'lib', pyver, 'site-packages','numpy','linalg'))

def set_nativ_env(env):
    pass
