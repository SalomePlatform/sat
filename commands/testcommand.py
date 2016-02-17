#!/usr/bin/env python
#-*- coding:utf-8 -*-

import subprocess

import src

# Define all possible option for config command :  sat config <options>
parser = src.options.Options()
parser.add_option('u', 'unique', 'boolean', 'unique', "TEST d'option.")
parser.add_option('v', 'value', 'string', 'value', "Appelle la commande config avec l'option value.")
parser.add_option('m', 'make', 'boolean', 'test_make', "Test d'une commande exterieure : make.")

def description():
    return _("Test d'une commande supplémentaire.")
    

def run(args, runner, logger):
    (options, args) = parser.parse_args(args)
    if options.unique:
        logger.write('unique\n')
    elif options.value:
        runner.cfg.VARS.user = 'TEST'
        runner.config('-v ' + options.value, logger)
    elif options.test_make:
        command = "make"
        logger.write("Execution of make\n", 3)
        res = subprocess.call(command, cwd=str('/tmp'), shell=True,
                      stdout=logger.logTxtFile, stderr=logger.logTxtFile)
        
        print(res)