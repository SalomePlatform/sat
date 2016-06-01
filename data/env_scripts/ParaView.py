#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    # keep only the first two version numbers
    ver = '.'.join(version.replace('-', '.').split('.')[:2])

    # BUG WITH 5.0_beta
    if ver == '5.0_beta':
        ver = '5.0'

    env.set('PVHOME', prereq_dir)
    env.set('VTKHOME', prereq_dir)  

    env.set('PVVERSION', ver)
    # [CMake GUI] Nouveau nom pour PVHOME = PARAVIEW_ROOT_DIR 22/03/2013
    # [CMake GUI] Nouveau nom pour PVVERSION = PARAVIEW_VERSION 22/03/2013
    env.set('PARAVIEW_ROOT_DIR', prereq_dir)

    env.set('PARAVIEW_VERSION', ver)
    version = env.get('PVVERSION') # = ${PVVERSION}

    set_paraview_env(env, version)
    set_vtk_env(env, version)

def set_nativ_env(env):
    if os.getenv("PVHOME") is None:
        raise Exception("PVHOME is not set")
    
    if os.getenv("PVVERSION") is None:
        raise Exception("PVVERSION is not set")

    version = env.get("PVVERSION")
    set_paraview_env(env, version)

def set_paraview_env(env, version):
    root = env.get('PVHOME')

    env.set('ParaView_DIR', os.path.join(root, 'lib', 'paraview-%s' % version))
    
    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('PATH', os.path.join(root, 'include', 'paraview-' + version))
    
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib', 'paraview-' + version))
    
    paralib = os.path.join(root, 'lib', 'paraview-' + version)
    env.prepend('PYTHONPATH', paralib)
    env.set('PV_PLUGIN_PATH', paralib)
    env.prepend('PYTHONPATH', os.path.join(paralib, 'site-packages'))
    env.prepend('PYTHONPATH', os.path.join(paralib, 'site-packages', 'vtk'))


def set_vtk_env(env, version):
    root = env.get('VTKHOME')
    pyver = 'python' + env.get('PYTHON_VERSION')

    env.prepend('PATH', os.path.join(root, 'bin'))
    env.prepend('LD_LIBRARY_PATH', os.path.join(root, 'lib'))
    env.prepend('PYTHONPATH', os.path.join(root, 'lib', pyver, 'site-packages'))
    #http://computer-programming-forum.com/57-tcl/1dfddc136afccb94.htm
    #Tcl treats the contents of that variable as a list. Be happy, for you can now use drive letters on windows.
    env.prepend('TCLLIBPATH', os.path.join(root, 'lib', 'vtk-5.0', 'tcl'), sep=" ")

    env.set('VTK_ROOT_DIR', root)
    if platform.system() == "Windows" :
        env.set('VTK_DIR', os.path.join(root, 'lib', 'cmake', 'paraview-' + version))
        env.prepend('VTK_ROOT_DIR', os.path.join(root, 'lib', 'cmake', 'paraview-' + version))
    else :
        env.set('VTK_DIR', os.path.join(root, 'lib', 'paraview-' + version))
        env.prepend('VTK_ROOT_DIR', os.path.join(root, 'lib', 'paraview-' + version))

    # 20 03 2013 compilation de PARAVIS basé sur paraview 3.98.1 et VTK 6
    if version == '3.98':
        cmake_dir = os.path.join(root, 'lib', 'cmake', 'paraview-' + version)
        env.set('VTK_DIR', cmake_dir)
    # fin

