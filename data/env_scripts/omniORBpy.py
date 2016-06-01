#!/usr/bin/env python
#-*- coding:utf-8 -*-

def set_env(env, prereq_dir, version):
    omniorb_root_dir = env.get('OMNIORB_ROOT_DIR')    
    env.set('OMNIORBPY_ROOT_DIR', omniorb_root_dir)    
    
def set_nativ_env(env):
    env.set('OMNIORBPY_ROOT_DIR',"/usr")
    pass

