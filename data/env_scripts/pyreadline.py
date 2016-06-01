#!/usr/bin/env python
#-*- coding:utf-8 -*-

# pyreadline install dir is PYTHON_ROOT_DIR, environment is set in Python.py

def set_env(env, prereq_dir, version):
	env.set('PYREADLINE_ROOT_DIR', env.get('PYTHON_ROOT_DIR'))
	
def set_nativ_env(env):
	env.set('PYREADLINE_ROOT_DIR', env.get('PYTHON_ROOT_DIR'))
	

