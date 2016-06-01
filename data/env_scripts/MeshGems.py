#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.add_comment("Here you can define your license parameters for MeshGems")
    env.add_comment("DISTENE license")

    if not env.is_defined("LICENSE_FILE"):
        script = os.path.join(os.path.dirname(os.path.realpath(__file__)), "distene_license.py")
        assert os.path.exists(script), "distene_license.py not found!"
        env.run_simple_env_script(script)

    env.set('MESHGEMSHOME', prereq_dir)
    env.set('MESHGEMS_ROOT_DIR', prereq_dir)    # update for cmake
    root = env.get('MESHGEMSHOME')

    if platform.system() == "Windows" :
        env.prepend('PATH', os.path.join(root, 'bin'))
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    else :
       
        libdir = "Linux_64"
    
        env.prepend('PATH', os.path.join(root, 'bin'))
        env.prepend('PATH', os.path.join(root, 'bin', libdir))
        env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib', libdir))



def set_nativ_env(env):
    pass
