#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path

def load_env(env):
    license_file = '/data/tmpsalome/salome/prerequis/install/LICENSE/dlim8.var.sh'
    if os.path.exists(license_file):
        env.add_line(1)
        env.add_comment("Set DISTENE License")
        env.set('DISTENE_LICENSE_FILE', 'Use global envvar: DLIM8VAR')
        env.set('DISTENE_LICENCE_FILE_FOR_MGCLEANER', license_file)
        env.set('DISTENE_LICENCE_FILE_FOR_YAMS', license_file)

        if os.access(license_file, os.R_OK):
            lines = open(license_file, "r").readlines()
            for line in lines:
                if line[:8] == "DLIM8VAR":
                    # line is: DLIM8VAR="<key>"\n
                    key = line.strip().split('=')[1]
                    key = key.strip().strip('"')
                    env.set("DLIM8VAR", key)
                    break
