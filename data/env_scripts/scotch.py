#!/usr/bin/env python
#-*- coding:utf-8 -*-

def set_env(env, prereq_dir, version):
    env.set('SCOTCHDIR', prereq_dir)
    env.set('SCOTCH_ROOT_DIR', prereq_dir)    # update for cmake

def set_nativ_env(env):
    env.set('SCOTCH_ROOT_DIR', '/usr')    # update for cmake
    env.set('SCOTCHDIR', '/usr')
    pass
