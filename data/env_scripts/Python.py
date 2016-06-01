#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path, platform

def set_env(env,prereq_dir,version,forBuild=None):
    # keep only the first two version numbers
    version = '.'.join(version.replace('-', '.').split('.')[:2])

    env.set('PYTHONHOME', prereq_dir)
        
    # [CMake KERNEL] Nouveau nom pour PYTHONHOME = PYTHON_ROOT_DIR 22/03/2013
    env.set('PYTHON_ROOT_DIR', prereq_dir)
    root = env.get('PYTHON_ROOT_DIR')
    
    env.prepend('PATH', root)
    env.prepend('PATH', os.path.join(root, 'bin'))

    l = []
    l.append(os.path.join(root, 'lib'))
    #l.append(os.path.join(root, 'lib', 'python' + version))
    
    if platform.system() == "Windows" :
        env.prepend('PATH', l)
        env.set('PYTHON_INCLUDE', os.path.join(root, 'include'))
        env.prepend('PYTHONPATH', os.path.join(root, 'Lib'))
        env.prepend('PYTHONPATH', os.path.join(root, 'lib','site-packages'))

        env.set('PYTHONBIN', os.path.join(root, 'python.exe'))  # needed for runSalome.py
    else :
        env.prepend('LD_LIBRARY_PATH', l)
        env.set('PYTHON_INCLUDE', os.path.join(root, 'include', 'python' + version))
        env.prepend('PYTHONPATH', os.path.join(root, 'lib', 'python' + version))
        env.prepend('PYTHONPATH', os.path.join(root, 'lib', 'python' + version, 'site-packages'))

        env.set('PYTHONBIN', os.path.join(root, 'bin','python'))  # needed for runSalome.py
    
    env.set('PYTHON_VERSION', version)


def set_nativ_env(env):
    import sys
    #env.set('PYTHONHOME',"%s.%s" % sys.version_info[0:2])
    env.set('PYTHON_ROOT_DIR', '/usr')
    env.set('PYTHON_VERSION', "%s.%s" % sys.version_info[0:2])
    pass
