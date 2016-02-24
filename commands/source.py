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
import shutil

import src

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('m', 'module', 'list2', 'modules',
    _('modules to get the sources. This option can be'
    ' passed several time to get the sources of several modules.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not prepare sample modules."))

def prepare_for_dev(config, module_info, source_dir, logger, pad):
    
    retcode = 'N\A'
    # if module sources dir does not exists in dev,
    # get it in checkout mode
    if not os.path.exists(module_info.source_dir):
        retcode = get_module_sources(config, module_info, True, source_dir, logger, pad, checkout=True)
        logger.write("\n", 3, False)
        logger.write(" " * (pad+2), 3, False) # +2 because module name is followed by ': '

    logger.write('dev: %s ... ' % src.printcolors.printcInfo(module_info.source_dir), 3, False)
    logger.flush()
    
    return retcode

def prepare_from_git(module_info, source_dir, logger, pad, is_dev=False):
    '''Prepares a module from git
    '''
    coflag = 'git'

    if is_dev and 'repo_dev' in module_info.git_info:
        coflag = src.printcolors.printcHighlight(coflag.upper())
        repo_git = module_info.git_info.repo_dev    
    else:
        repo_git = module_info.git_info.repo    
        
  
    logger.write('%s:%s' % (coflag, src.printcolors.printcInfo(repo_git)), 3, False)
    logger.write(' ' * (pad + 50 - len(repo_git)), 3, False)
    logger.write(' tag:%s' % src.printcolors.printcInfo(module_info.git_info.tag), 3, False)
    logger.write(' %s. ' % ('.' * (10 - len(module_info.git_info.tag))), 3, False)
    logger.flush()
    logger.write('\n', 5, False)
    retcode = src.system.git_extract(repo_git,
                                 module_info.git_info.tag,
                                 source_dir, logger)
    return retcode

def prepare_from_archive(module_info, source_dir, logger):
    # check archive exists
    if not os.path.exists(module_info.archive_info.archive_name):
        raise src.SatException(_("Archive not found: '%s'") % module_info.archive_info.archive_name)

    logger.write('arc:%s ... ' % src.printcolors.printcInfo(module_info.archive_info.archive_name), 3, False)
    logger.flush()
    retcode, NameExtractedDirectory = src.system.archive_extract(module_info.archive_info.archive_name,
                                     source_dir.dir(), logger)
    
    # Rename the source directory if it does not match with module_info.source_dir
    if NameExtractedDirectory.replace('/', '') != os.path.basename(module_info.source_dir):
        shutil.move(os.path.join(os.path.dirname(module_info.source_dir), NameExtractedDirectory), module_info.source_dir)
    
    return retcode

def get_module_sources(config, module_info, is_dev, source_dir, logger, pad, checkout=False):
    '''Get the module sources.
    
    '''
    if not checkout and is_dev:
        return prepare_for_dev(config, module_info, source_dir, logger, pad)

    if module_info.get_method == "git":
        return prepare_from_git(module_info, source_dir, logger, pad, is_dev)

    if module_info.get_method == "archive":
        return prepare_from_archive(module_info, source_dir, logger)
    '''
    if module_info.get_method == "cvs":
        cvs_user = common.get_cfg_param(module_info.cvs_info, "cvs_user", config.USER.cvs_user)
        return prepare_from_cvs(cvs_user, module_info, source_dir, checkout, logger, pad)

    if module_info.get_method == "svn":
        svn_user = common.get_cfg_param(module_info.svn_info, "svn_user", config.USER.svn_user)
        return prepare_from_svn(svn_user, module_info, source_dir, checkout, logger)
        
    if module_info.get_method == "dir":
        return prepare_from_dir(module_info, source_dir, logger)
    '''
    
    if len(module_info.get_method) == 0:
        # skip
        logger.write('%s ...' % _("ignored"), 3, False)
        return True

    #
    logger.write(_("Unknown get_mehtod %(get)s for module %(module)s") % \
        { 'get': module_info.get_method, 'module': module_info.name }, 3, False)
    logger.write(" ... ", 3, False)
    logger.flush()
    return False

def get_all_module_sources(config, modules, logger):
    '''Get all the module sources.
    
    '''

    results = dict()
    good_result = 0

    max_module_name_len = 1
    if len(modules) > 0:
        max_module_name_len = max(map(lambda l: len(l), modules[0])) + 4
    for module in modules:
        module_name = module[0]
        module_info = module[1]
        source_dir = src.Path(module_info.source_dir)

        logger.write('%s: ' % src.printcolors.printcLabel(module_name), 3)
        logger.write(' ' * (max_module_name_len - len(module_name)), 3, False)
        logger.write("\n", 4, False)
        
        is_dev = "dev_modules" in config.APPLICATION and module_name in config.APPLICATION.dev_modules
        if source_dir.exists() and not is_dev:
            logger.write("  " + _('remove %s') % source_dir, 4)
            logger.write("\n  ", 4, False)
            source_dir.rm()

        retcode = get_module_sources(config, module_info, is_dev, source_dir, logger, max_module_name_len, checkout=False)
        
        '''
        if 'no_rpath' in module_info.keys():
            if module_info.no_rpath:
                hack_no_rpath(config, module_info, logger)
        '''

        # show results
        results[module_name] = retcode
        if retcode == 'N\A':
            res =src.printcolors.printc(src.OK_STATUS) + src.printcolors.printcWarning(_(' source directory already exists'))
            good_result = good_result + 1
        elif retcode:
            res = src.OK_STATUS
            good_result = good_result + 1
        else:
            res = src.KO_STATUS

        logger.write('%s\n' % src.printcolors.printc(res), 3, False)

    return good_result, results

def run(args, runner, logger):
    '''method that is called when salomeTools is called with source parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    logger.write(_('Preparing sources of product %s\n') % 
                        src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    src.printcolors.print_value(logger, 'out_dir', 
                                runner.cfg.APPLICATION.out_dir, 2)
    logger.write("\n", 2, False)

    if options.modules is None:
        modules = runner.cfg.APPLICATION.modules
    else:
        modules = options.modules
        for m in modules:
            if m not in runner.cfg.APPLICATION.modules:
                raise src.SatException(_("Module %(module)s not defined in product %(product)s") %
                    { 'module': m, 'product': runner.cfg.VARS.product} )
    
    modules_infos = src.module.get_modules_infos(modules, runner.cfg)

    
    if options.no_sample:
        modules_infos = filter(lambda l: not src.module.module_is_sample(l[1]), 
                         modules_infos)

    good_result, results = get_all_module_sources(runner.cfg, modules_infos, logger)

    status = src.OK_STATUS
    details = []

    logger.write("\n", 2, False)
    if good_result == len(modules):
        res_count = "%d / %d" % (good_result, good_result)
    else:
        status = src.KO_STATUS
        res_count = "%d / %d" % (good_result, len(modules))

        for module in results:
            if results[module] == 0 or results[module] is None:
                details.append(module)

    result = len(modules) - good_result

    # write results
    logger.write(_("Preparing of product's sources:"), 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)

    if len(details) > 0:
        logger.write(_("Following sources haven't been prepared:\n"), 2)
        logger.write(" ".join(details), 2)
        logger.write("\n", 2, False)

    return result
