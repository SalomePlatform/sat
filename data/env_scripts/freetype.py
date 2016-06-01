#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os

def set_env(env, prereq_dir, version):
    env.set('FREETYPEDIR', prereq_dir)
    env.set('FREETYPE_ROOT_DIR', prereq_dir)    # update for cmake
    env.prepend('PATH', os.path.join(env.get('FREETYPE_ROOT_DIR'), 'bin'))
    env.prepend('INCLUDE', os.path.join(env.get('FREETYPE_ROOT_DIR'), 'include'))
    env.prepend('CPLUS_INCLUDE_PATH', os.path.join(prereq_dir, 'include', 'freetype2'))

def set_nativ_env(env):
    env.set('FREETYPE_ROOT_DIR', '/usr')    # update for cmake
    env.set('FREETYPEDIR', '/usr')
    pass
