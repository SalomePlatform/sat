#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2012  CEA/DEN
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

import os

import src

# Define all possible option for the shell command :  sat base <options>
parser = src.options.Options()
parser.add_option('s', 'set', 'string', 'base_path',
    _('The path directory to use as base.'), None)

def set_base(config, path, site_file_path, logger):
    """ Edit the site.pyconf file and change the base path

    :param config Config: The global configuration.    
    :param path src.Path: The path to put in the site.pyconf file.
    :param site_file_path Str: The path to the site.pyconf file.
    :param logger Logger: The logger instance.
    :return: 0 if all is OK, else 1
    :rtype: int
    """
    # Update the site.pyconf file
    try:
        site_pyconf_cfg = src.pyconf.Config(site_file_path)
        site_pyconf_cfg.SITE.base = str(path)
        ff = open(site_file_path, 'w')
        site_pyconf_cfg.__save__(ff, 1)
        ff.close()
        config.SITE.base = str(path)
    except Exception as e:
        err = str(e)
        msg = _("Unable to update the site.pyconf file: %s\n" % err)
        logger.write(msg, 1)
        return 1
    
    display_base_path(config, logger)
    
    return 0


def display_base_path(config, logger):
    """ Display the base path

    :param config Config: The global configuration.    
    :param logger Logger: The logger instance.
    """
    info = [(_("Base path"), config.SITE.base)]
    src.print_info(logger, info)

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the base command description.
    :rtype: str
    '''
    return _("Display or set the base where to put installations of base "
             "products")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with base parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # Get the path to the site.pyconf file that contain the base path
    site_file_path = os.path.join(runner.cfg.VARS.salometoolsway,
                                  "data",
                                  "site.pyconf")
    
    # If the option set is passed
    if options.base_path:
        # Get the path
        path = src.Path(options.base_path)
        
        # If it is a file, do nothing and return error
        if path.isfile():
            msg = _("Error: The given path is a file. Please provide a path to "
                    "a directory")
            logger.write(src.printcolors.printcError(msg), 1)
            return 1
        
        # If it is an existing directory, set the base to it
        if path.exists() and path.isdir():
            # Set the base in the site.pyconf file
            res = set_base(runner.cfg, path, site_file_path, logger)
            return res
        
        # Try to create the given path
        try:
            src.ensure_path_exists(str(path))
        except Exception as e:
            err = src.printcolors.printcError(str(e))
            msg = _("Unable to create the directory %s: %s\n" % (str(path),
                                                                 err))
            logger.write(msg, 1)
            return 1
        
        # Set the base in the site.pyconf file
        res = set_base(runner.cfg, path, site_file_path, logger)
        return res
    
    # Display the base that is in the site.pyconf file
    display_base_path(runner.cfg, logger)
    if not options.base_path:
        logger.write(_("To change the value of the base path, use the --set"
                       " option.\n"), 2)
    
    return