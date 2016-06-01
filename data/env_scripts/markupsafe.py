#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import platform

def set_env(env, prereq_dir, version):
    env.set("MARKUPSAFE_ROOT_DIR",prereq_dir)
    env.prepend('PATH', os.path.join(prereq_dir, 'bin'))

    if platform.system() == "Windows" :
        env.prepend('PYTHONPATH',os.path.join(prereq_dir, 'lib', 'site-packages'))
    else:
        versionPython = env.get('PYTHON_VERSION')
        env.prepend('PYTHONPATH',os.path.join(prereq_dir, 'lib', 'python' + versionPython, 'site-packages'))
        env.prepend('PYTHONPATH',os.path.join(prereq_dir, 'bin'))
    pass

def set_nativ_env(env):
    pass
