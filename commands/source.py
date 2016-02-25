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
    _('modules from which to get the sources. This option can be'
    ' passed several time to get the sources of several modules.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not get sources from sample modules."))
parser.add_option('f', 'force', 'boolean', 'force', 
    _("force to get the sources of the modules in development mode."))

def prepare_for_dev(config, module_info, source_dir, force, logger, pad):
    '''The method called if the module is in development mode
    
    :param config Config: The global configuration
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param force boolean: True if the --force option was invoked
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    retcode = 'N\A'
    # if the module source directory does not exist,
    # get it in checkout mode, else, do not do anything
    # unless the force option is invoked
    if not os.path.exists(module_info.source_dir) or force:
        # Call the function corresponding to get the sources with True checkout
        retcode = get_module_sources(config, 
                                     module_info, 
                                     True, 
                                     source_dir,
                                     force, 
                                     logger, 
                                     pad, 
                                     checkout=True)
        logger.write("\n", 3, False)
        # +2 because module name is followed by ': '
        logger.write(" " * (pad+2), 3, False) 
    
    logger.write('dev: %s ... ' % 
                 src.printcolors.printcInfo(module_info.source_dir), 3, False)
    logger.flush()
    
    return retcode

def get_sources_from_git(module_info, source_dir, logger, pad, is_dev=False):
    '''The method called if the module is to be get in git mode
    
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :param is_dev boolean: True if the module is in development mode
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # The str to display
    coflag = 'git'

    # Get the repository address. (from repo_dev key if the module is 
    # in dev mode.
    if is_dev and 'repo_dev' in module_info.git_info:
        coflag = src.printcolors.printcHighlight(coflag.upper())
        repo_git = module_info.git_info.repo_dev    
    else:
        repo_git = module_info.git_info.repo    
        
    # Display informations
    logger.write('%s:%s' % (coflag, src.printcolors.printcInfo(repo_git)), 3, 
                 False)
    logger.write(' ' * (pad + 50 - len(repo_git)), 3, False)
    logger.write(' tag:%s' % src.printcolors.printcInfo(
                                                    module_info.git_info.tag), 
                 3,
                 False)
    logger.write(' %s. ' % ('.' * (10 - len(module_info.git_info.tag))), 3, 
                 False)
    logger.flush()
    logger.write('\n', 5, False)
    # Call the system function that do the extraction in git mode
    retcode = src.system.git_extract(repo_git,
                                 module_info.git_info.tag,
                                 source_dir, logger)
    return retcode

def get_sources_from_archive(module_info, source_dir, logger):
    '''The method called if the module is to be get in archive mode
    
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # check archive exists
    if not os.path.exists(module_info.archive_info.archive_name):
        raise src.SatException(_("Archive not found: '%s'") % 
                               module_info.archive_info.archive_name)

    logger.write('arc:%s ... ' % 
                 src.printcolors.printcInfo(module_info.archive_info.archive_name),
                 3, 
                 False)
    logger.flush()
    # Call the system function that do the extraction in archive mode
    retcode, NameExtractedDirectory = src.system.archive_extract(
                                    module_info.archive_info.archive_name,
                                    source_dir.dir(), logger)
    
    # Rename the source directory if 
    # it does not match with module_info.source_dir
    if (NameExtractedDirectory.replace('/', '') != 
            os.path.basename(module_info.source_dir)):
        shutil.move(os.path.join(os.path.dirname(module_info.source_dir), 
                                 NameExtractedDirectory), 
                    module_info.source_dir)
    
    return retcode

def get_sources_from_cvs(user, module_info, source_dir, checkout, logger, pad):
    '''The method called if the module is to be get in cvs mode
    
    :param user str: The user to use in for the cvs command
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param checkout boolean: If True, get the source in checkout mode
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # Get the protocol to use in the command
    if "protocol" in module_info.cvs_info:
        protocol = module_info.cvs_info.protocol
    else:
        protocol = "pserver"
    
    # Construct the line to display
    if "protocol" in module_info.cvs_info:
        cvs_line = "%s:%s@%s:%s" % \
            (protocol, user, module_info.cvs_info.server, 
             module_info.cvs_info.module_base)
    else:
        cvs_line = "%s / %s" % (module_info.cvs_info.server, 
                                module_info.cvs_info.module_base)

    coflag = 'cvs'
    if checkout: coflag = src.printcolors.printcHighlight(coflag.upper())

    logger.write('%s:%s' % (coflag, src.printcolors.printcInfo(cvs_line)), 
                 3, 
                 False)
    logger.write(' ' * (pad + 50 - len(cvs_line)), 3, False)
    logger.write(' src:%s' % 
                 src.printcolors.printcInfo(module_info.cvs_info.source), 
                 3, 
                 False)
    logger.write(' ' * (pad + 1 - len(module_info.cvs_info.source)), 3, False)
    logger.write(' tag:%s' % 
                    src.printcolors.printcInfo(module_info.cvs_info.tag), 
                 3, 
                 False)
    # at least one '.' is visible
    logger.write(' %s. ' % ('.' * (10 - len(module_info.cvs_info.tag))), 
                 3, 
                 False) 
    logger.flush()
    logger.write('\n', 5, False)

    # Call the system function that do the extraction in cvs mode
    retcode = src.system.cvs_extract(protocol, user,
                                 module_info.cvs_info.server,
                                 module_info.cvs_info.module_base,
                                 module_info.cvs_info.tag,
                                 module_info.cvs_info.source,
                                 source_dir, logger, checkout)
    return retcode

def get_sources_from_svn(user, module_info, source_dir, checkout, logger):
    '''The method called if the module is to be get in svn mode
    
    :param user str: The user to use in for the svn command
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param checkout boolean: If True, get the source in checkout mode
    :param logger Logger: The logger instance to use for the display and logging
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    coflag = 'svn'
    if checkout: coflag = src.printcolors.printcHighlight(coflag.upper())

    logger.write('%s:%s ... ' % (coflag, 
                                 src.printcolors.printcInfo(
                                            module_info.svn_info.repo)), 
                 3, 
                 False)
    logger.flush()
    logger.write('\n', 5, False)
    # Call the system function that do the extraction in svn mode
    retcode = src.system.svn_extract(user, 
                                     module_info.svn_info.repo, 
                                     module_info.svn_info.tag,
                                     source_dir, 
                                     logger, 
                                     checkout)
    return retcode

def get_sources_from_dir(module_info, source_dir, logger):
    '''The method called if the module is to be get in dir mode
    
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # Check if it is a symlink?
    use_link = ('symlink' in module_info.dir_info and 
                module_info.dir_info.symlink)
    dirflag = 'dir'
    if use_link: dirflag = 'lnk'

    # check that source exists if it is not a symlink
    if (not use_link) and (not os.path.exists(module_info.dir_info.dir)):
        raise src.SatException(_("Source directory not found: '%s'") % 
                               module_info.dir_info.dir)

    logger.write('%s:%s ... ' % 
                 (dirflag, src.printcolors.printcInfo(module_info.dir_info.dir)),
                 3, 
                 False)
    logger.flush()

    if use_link:
        retcode = src.Path(source_dir).symlink(module_info.dir_info.dir)
    else:
        retcode = src.Path(module_info.dir_info.dir).copy(source_dir)

    return retcode

def get_module_sources(config, 
                       module_info, 
                       is_dev, 
                       source_dir,
                       force,
                       logger, 
                       pad, 
                       checkout=False):
    '''Get the module sources.
    
    :param config Config: The global configuration
    :param module_info Config: The configuration specific to 
                               the module to be prepared
    :param is_dev boolean: True if the module is in development mode
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param force boolean: True if the --force option was invoked
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :param checkout boolean: If True, get the source in checkout mode
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    if not checkout and is_dev:
        return prepare_for_dev(config, module_info, source_dir, force, logger, pad)

    if module_info.get_method == "git":
        return get_sources_from_git(module_info, source_dir, logger, pad, 
                                    is_dev)

    if module_info.get_method == "archive":
        return get_sources_from_archive(module_info, source_dir, logger)
    
    if module_info.get_method == "cvs":
        cvs_user = config.USER.cvs_user
        return get_sources_from_cvs(cvs_user, 
                                    module_info, 
                                    source_dir, 
                                    checkout, 
                                    logger,
                                    pad)

    if module_info.get_method == "svn":
        svn_user = config.USER.svn_user
        return get_sources_from_svn(svn_user, module_info, source_dir, 
                                    checkout,
                                    logger)
   
    if module_info.get_method == "dir":
        return get_sources_from_dir(module_info, source_dir, logger)
    
    if len(module_info.get_method) == 0:
        # skip
        logger.write('%s ...' % _("ignored"), 3, False)
        return True

    # if the get_method is not in [git, archive, cvs, svn, dir]
    logger.write(_("Unknown get_mehtod %(get)s for module %(module)s") % \
        { 'get': module_info.get_method, 'module': module_info.name }, 3, False)
    logger.write(" ... ", 3, False)
    logger.flush()
    return False

def get_all_module_sources(config, modules, force, logger):
    '''Get all the module sources.
    
    :param config Config: The global configuration
    :param modules List: The list of tuples (module name, module informations)
    :param force boolean: True if the --force option was invoked
    :param logger Logger: The logger instance to be used for the logging
    :return: the tuple (number of success, dictionary module_name/success_fail)
    :rtype: (int,dict)
    '''

    # Initialize the variables that will count the fails and success
    results = dict()
    good_result = 0

    # Get the maximum name length in order to format the terminal display
    max_module_name_len = 1
    if len(modules) > 0:
        max_module_name_len = max(map(lambda l: len(l), modules[0])) + 4
    
    # The loop on all the modules from which to get the sources
    for module_name, module_info in modules:
        # get module name, module informations and the directory where to put
        # the sources
        source_dir = src.Path(module_info.source_dir)

        # display and log
        logger.write('%s: ' % src.printcolors.printcLabel(module_name), 3)
        logger.write(' ' * (max_module_name_len - len(module_name)), 3, False)
        logger.write("\n", 4, False)
        
        # Remove the existing source directory if 
        # the module is not in development mode 
        is_dev = ("dev_modules" in config.APPLICATION and 
                  module_name in config.APPLICATION.dev_modules)
        if source_dir.exists() and not is_dev:
            logger.write("  " + _('remove %s') % source_dir, 4)
            logger.write("\n  ", 4, False)
            source_dir.rm()

        # Call to the function that get the sources for one module
        retcode = get_module_sources(config, 
                                     module_info, 
                                     is_dev, 
                                     source_dir,
                                     force, 
                                     logger, 
                                     max_module_name_len, 
                                     checkout=False)
        
        '''
        if 'no_rpath' in module_info.keys():
            if module_info.no_rpath:
                hack_no_rpath(config, module_info, logger)
        '''

        # show results
        results[module_name] = retcode
        if retcode == 'N\A':
            # The case where the module was not prepared because it is 
            # in development mode
            res =(src.printcolors.printc(src.OK_STATUS) + 
                    src.printcolors.printcWarning(_(
                                    ' source directory already exists')))
            good_result = good_result + 1
        elif retcode:
            # The case where it succeed
            res = src.OK_STATUS
            good_result = good_result + 1
        else:
            # The case where it failed
            res = src.KO_STATUS
        
        # print the result
        logger.write('%s\n' % src.printcolors.printc(res), 3, False)

    return good_result, results

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the source command description.
    :rtype: str
    '''
    return _("The source command gets the sources of the application modules "
             "from cvs, git, an archive or a directory..")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with source parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Print some informations
    logger.write(_('Preparing sources of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    src.printcolors.print_value(logger, 'out_dir', 
                                runner.cfg.APPLICATION.out_dir, 2)
    logger.write("\n", 2, False)
    
    # Get the force option if it was passed
    force = options.force
    if force:
        msg = _("Warning: the --force option has effect only "
                "on modules in development mode\n\n")
        logger.write(src.printcolors.printcWarning(msg))
    
    # Get the modules to be prepared, regarding the options
    if options.modules is None:
        # No options, get all modules sources
        modules = runner.cfg.APPLICATION.modules
    else:
        # if option --modules, check that all modules of the command line
        # are present in the application.
        modules = options.modules
        for m in modules:
            if m not in runner.cfg.APPLICATION.modules:
                raise src.SatException(_("Module %(module)s "
                            "not defined in appplication %(application)s") %
                { 'module': m, 'application': runner.cfg.VARS.application} )
    
    # Construct the list of tuple containing 
    # the modules name and their definition
    modules_infos = src.module.get_modules_infos(modules, runner.cfg)

    # if the --no_sample option is invoked, suppress the sample modules from 
    # the list
    if options.no_sample:
        modules_infos = filter(lambda l: not src.module.module_is_sample(l[1]),
                         modules_infos)
    
    # Call to the function that gets all the sources
    good_result, results = get_all_module_sources(runner.cfg, 
                                                  modules_infos,
                                                  force,
                                                  logger)

    # Display the results (how much passed, how much failed, etc...)
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
    logger.write(_("Getting sources of the application:"), 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)

    if len(details) > 0:
        logger.write(_("Following sources haven't been get:\n"), 2)
        logger.write(" ".join(details), 2)
        logger.write("\n", 2, False)

    return result
