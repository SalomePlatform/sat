#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def set_env(env, prereq_dir, version):
    env.set('LAPACKHOME', prereq_dir)
    env.set('LAPACK_ROOT_DIR', prereq_dir)
    env.set('LAPACK_SRC', os.path.join(prereq_dir,'SRC'))
    #env.set('LAPACK', os.path.join(prereq_dir))
    env.set('BLAS_SRC', os.path.join(prereq_dir,'BLAS','SRC'))
    root = env.get('LAPACKHOME')
    
    env.prepend('PATH', os.path.join(root, 'lapacke','include'))
    env.prepend('PATH', os.path.join(root, 'lib'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    env.prepend('PYTHONPATH', os.path.join(root, 'Lib'))

    # FOR NUMPY AND SCIPY
    env.set('BLAS', os.path.join(root, 'lib'))
    env.set('LAPACK', os.path.join(root, 'lib'))
    env.set('ATLAS', os.path.join(root, 'lib'))
    

def set_nativ_env(env):
    env.set('LAPACKHOME', '/usr')
    pass
