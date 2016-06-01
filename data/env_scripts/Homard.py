#!/usr/bin/env python
#-*- coding:utf-8 -*-

def set_env(env, prereq_dir, version):
    env.set('HOMARD_REP_EXE', prereq_dir)
    root = env.get('HOMARD_REP_EXE')
    env.set('HOMARD_EXE', 'homard')
    
    env.prepend('PATH', root)

def set_nativ_env(env):
    pass
