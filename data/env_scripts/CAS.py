#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path
import platform

def set_env(env, prereq_dir, version):
    env.set('CASROOT', prereq_dir)
    root = env.get('CASROOT')
    
    # [CMake GUI] Nouveau nom pour CASROOT = CAS_ROOT_DIR 22/03/2013
    env.set('CAS_ROOT_DIR', prereq_dir)

    env.prepend('PATH', os.path.join(root, 'bin'))

    l = []
    l.append(os.path.join(root, 'lib'))
    l.append(os.path.join(root, 'lin', 'lib'))
    if platform.system()=="Windows" :
        l.append(os.path.join(root, 'win64', 'vc10' ,'lib'))
        l.append(os.path.join(root, 'win64', 'vc10' ,'bin'))
        l.append(os.path.join(root, 'inc'))
        env.prepend('PATH', l)
    else :
        env.prepend('LD_LIBRARY_PATH', l)

    env.set('CSF_UnitsLexicon', os.path.join(root, 'src', 'UnitsAPI', 'Lexi_Expr.dat'))
    env.set('CSF_UnitsDefinition', os.path.join(root, 'src', 'UnitsAPI', 'Units.dat'))
    env.set('CSF_SHMessage', os.path.join(root, 'src', 'SHMessage'))
    env.set('CSF_XSMessage', os.path.join(root, 'src', 'XSMessage'))
    env.set('CSF_MDTVFontDirectory', os.path.join(root, 'src', 'FontMFT'))
    env.set('CSF_MDTVTexturesDirectory', os.path.join(root, 'src', 'Textures'))
    env.set('MMGT_REENTRANT', "1")
    env.set('CSF_StandardDefaults', os.path.join(root, 'src', 'StdResource'))
    env.set('CSF_PluginDefaults', os.path.join(root, 'src', 'StdResource'))
    env.prepend('PATH', root)

    env.set('LIB', '$LD_LIBRARY_PATH')

def set_nativ_env(env):
    pass
