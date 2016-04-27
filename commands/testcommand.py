#!/usr/bin/env python
#-*- coding:utf-8 -*-

import src

# Define all possible option for testcommand command :  sat testcommand <options>
parser = src.options.Options()
parser.add_option('p', 'product', 'list2', 'nb_proc',
    _('products to get the sources. This option can be'
    ' passed several time to get the sources of several products.'))

parser.add_option('', 'dd', 'list2', 'makeflags',
    _('products to get the sources. This option can be'
    ' passed several time to get the sources of several products.'))

def description():
    return _("Test d'une commande supplémentaire.")
    

def run(args, runner, logger):
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )
    
    pi = src.product.get_product_config(runner.cfg, 'PRODUCT_GIT')
    
    builder = src.compilation.Builder(runner.cfg, logger, options, pi)
    
    builder.prepare()
    
    builder.cmake()
    
    builder.make()