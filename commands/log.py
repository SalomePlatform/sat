#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import shutil

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('t', 'terminal', 'boolean', 'terminal', "Terminal log.")



def description():
    return _("Gives access to logs of salomeTools.")    

def run(args, runner):
    (options, args) = parser.parse_args(args)
    if options.terminal:
        print('terminal')
    
    # Find stylesheet Directory and files
    xslDir = os.path.join(runner.cfg.VARS.srcDir, 'xsl')
    xslCommand = os.path.join(xslDir, "command.xsl")
    xslHat = os.path.join(xslDir, "hat.xsl")
    imgLogo = os.path.join(xslDir, "LOGO-SAT.png")

    # get the log direcory. If there is an application, it is in cfg.APPLICATION.out_dir, else in user directory
    logDir = runner.cfg.VARS.logDir
    
    # copy the stylesheet in the log directory
    shutil.copy2(xslCommand, logDir)
    shutil.copy2(xslHat, logDir)
    shutil.copy2(imgLogo, logDir)
    
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    if 'APPLICATION' in runner.cfg:
        src.xmlManager.update_hat_xml(runner.cfg.VARS.logDir, runner.cfg.VARS.application)
    else:
        src.xmlManager.update_hat_xml(runner.cfg.VARS.logDir)
    
    src.system.show_in_editor(runner.cfg.USER.browser, xmlHatFilePath)