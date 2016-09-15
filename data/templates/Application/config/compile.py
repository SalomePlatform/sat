#!/usr/bin/env python
#-*- coding:utf-8 -*-

# This script is used to build the application module.
# First, it copies the content of the sources directory to the install directory.
# Then it runs 'lrelease' to build the resources.

import subprocess

import src

def compil(config, builder, logger):
    builder.prepare()
    if not builder.source_dir.smartcopy(builder.install_dir):
        raise src.SatException(_("Error when copying %s sources to install dir") % builder.product_info.name)
    
    # test lrelease #.pyconf needs in ..._APPLI pre_depend : ['qt']
    command = "which lrelease" 
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=builder.build_environ.environ.environ).communicate()
    if res[1] != "": #an error occured
        logger.write("ERROR: %s" % res[1])
        builder.log(res[1]+"\n")
        return 1
    
    # run lrelease
    command = "lrelease *.ts"
    res = subprocess.call(command,
                          shell=True,
                          cwd=str(builder.install_dir + "resources"),
                          env=builder.build_environ.environ.environ,
                          stdout=logger.logTxtFile,
                          stderr=subprocess.STDOUT)
    if res != 0:
        res = 1
    
    return res
