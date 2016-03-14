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
import prepare

# Define all possible option for log command :  sat log <options>
parser = src.options.Options()
parser.add_option('p', 'product', 'list2', 'products',
    _('products from which to get the sources. This option can be'
    ' passed several time to get the sources of several products.'))
parser.add_option('', 'no_sample', 'boolean', 'no_sample', 
    _("do not get sources from sample products."))
parser.add_option('f', 'force', 'boolean', 'force', 
    _("force to get the sources of the products in development mode."))

def get_source_for_dev(config, product_info, source_dir, force, logger, pad):
    '''The method called if the product is in development mode
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param force boolean: True if the --force option was invoked
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    retcode = 'N\A'
    # if the product source directory does not exist,
    # get it in checkout mode, else, do not do anything
    # unless the force option is invoked
    if not os.path.exists(product_info.source_dir) or force:
        # Call the function corresponding to get the sources with True checkout
        retcode = get_product_sources(config, 
                                     product_info, 
                                     True, 
                                     source_dir,
                                     force, 
                                     logger, 
                                     pad, 
                                     checkout=True)
        logger.write("\n", 3, False)
        # +2 because product name is followed by ': '
        logger.write(" " * (pad+2), 3, False) 
    
    logger.write('dev: %s ... ' % 
                 src.printcolors.printcInfo(product_info.source_dir), 3, False)
    logger.flush()
    
    return retcode

def get_source_from_git(product_info, source_dir, logger, pad, is_dev=False):
    '''The method called if the product is to be get in git mode
    
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :param is_dev boolean: True if the product is in development mode
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # The str to display
    coflag = 'git'

    # Get the repository address. (from repo_dev key if the product is 
    # in dev mode.
    if is_dev and 'repo_dev' in product_info.git_info:
        coflag = src.printcolors.printcHighlight(coflag.upper())
        repo_git = product_info.git_info.repo_dev    
    else:
        repo_git = product_info.git_info.repo    
        
    # Display informations
    logger.write('%s:%s' % (coflag, src.printcolors.printcInfo(repo_git)), 3, 
                 False)
    logger.write(' ' * (pad + 50 - len(repo_git)), 3, False)
    logger.write(' tag:%s' % src.printcolors.printcInfo(
                                                    product_info.git_info.tag), 
                 3,
                 False)
    logger.write(' %s. ' % ('.' * (10 - len(product_info.git_info.tag))), 3, 
                 False)
    logger.flush()
    logger.write('\n', 5, False)
    # Call the system function that do the extraction in git mode
    retcode = src.system.git_extract(repo_git,
                                 product_info.git_info.tag,
                                 source_dir, logger)
    return retcode

def get_source_from_archive(product_info, source_dir, logger):
    '''The method called if the product is to be get in archive mode
    
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param logger Logger: The logger instance to use for the display and logging
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # check archive exists
    if not os.path.exists(product_info.archive_info.archive_name):
        raise src.SatException(_("Archive not found: '%s'") % 
                               product_info.archive_info.archive_name)

    logger.write('arc:%s ... ' % 
                 src.printcolors.printcInfo(product_info.archive_info.archive_name),
                 3, 
                 False)
    logger.flush()
    # Call the system function that do the extraction in archive mode
    retcode, NameExtractedDirectory = src.system.archive_extract(
                                    product_info.archive_info.archive_name,
                                    source_dir.dir(), logger)
    
    # Rename the source directory if 
    # it does not match with product_info.source_dir
    if (NameExtractedDirectory.replace('/', '') != 
            os.path.basename(product_info.source_dir)):
        shutil.move(os.path.join(os.path.dirname(product_info.source_dir), 
                                 NameExtractedDirectory), 
                    product_info.source_dir)
    
    return retcode

def get_source_from_cvs(user, product_info, source_dir, checkout, logger, pad):
    '''The method called if the product is to be get in cvs mode
    
    :param user str: The user to use in for the cvs command
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param source_dir Path: The Path instance corresponding to the 
                            directory where to put the sources
    :param checkout boolean: If True, get the source in checkout mode
    :param logger Logger: The logger instance to use for the display and logging
    :param pad int: The gap to apply for the terminal display
    :return: True if it succeed, else False
    :rtype: boolean
    '''
    # Get the protocol to use in the command
    if "protocol" in product_info.cvs_info:
        protocol = product_info.cvs_info.protocol
    else:
        protocol = "pserver"
    
    # Construct the line to display
    if "protocol" in product_info.cvs_info:
        cvs_line = "%s:%s@%s:%s" % \
            (protocol, user, product_info.cvs_info.server, 
             product_info.cvs_info.product_base)
    else:
        cvs_line = "%s / %s" % (product_info.cvs_info.server, 
                                product_info.cvs_info.product_base)

    coflag = 'cvs'
    if checkout: coflag = src.printcolors.printcHighlight(coflag.upper())

    logger.write('%s:%s' % (coflag, src.printcolors.printcInfo(cvs_line)), 
                 3, 
                 False)
    logger.write(' ' * (pad + 50 - len(cvs_line)), 3, False)
    logger.write(' src:%s' % 
                 src.printcolors.printcInfo(product_info.cvs_info.source), 
                 3, 
                 False)
    logger.write(' ' * (pad + 1 - len(product_info.cvs_info.source)), 3, False)
    logger.write(' tag:%s' % 
                    src.printcolors.printcInfo(product_info.cvs_info.tag), 
                 3, 
                 False)
    # at least one '.' is visible
    logger.write(' %s. ' % ('.' * (10 - len(product_info.cvs_info.tag))), 
                 3, 
                 False) 
    logger.flush()
    logger.write('\n', 5, False)

    # Call the system function that do the extraction in cvs mode
    retcode = src.system.cvs_extract(protocol, user,
                                 product_info.cvs_info.server,
                                 product_info.cvs_info.product_base,
                                 product_info.cvs_info.tag,
                                 product_info.cvs_info.source,
                                 source_dir, logger, checkout)
    return retcode

def get_source_from_svn(user, product_info, source_dir, checkout, logger):
    '''The method called if the product is to be get in svn mode
    
    :param user str: The user to use in for the svn command
    :param product_info Config: The configuration specific to 
                               the product to be prepared
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
                                            product_info.svn_info.repo)), 
                 3, 
                 False)
    logger.flush()
    logger.write('\n', 5, False)
    # Call the system function that do the extraction in svn mode
    retcode = src.system.svn_extract(user, 
                                     product_info.svn_info.repo, 
                                     product_info.svn_info.tag,
                                     source_dir, 
                                     logger, 
                                     checkout)
    return retcode

def get_product_sources(config, 
                       product_info, 
                       is_dev, 
                       source_dir,
                       force,
                       logger, 
                       pad, 
                       checkout=False):
    '''Get the product sources.
    
    :param config Config: The global configuration
    :param product_info Config: The configuration specific to 
                               the product to be prepared
    :param is_dev boolean: True if the product is in development mode
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
        return get_source_for_dev(config, 
                                   product_info, 
                                   source_dir, 
                                   force, 
                                   logger, 
                                   pad)

    if product_info.get_source == "git":
        return get_source_from_git(product_info, source_dir, logger, pad, 
                                    is_dev)

    if product_info.get_source == "archive":
        return get_source_from_archive(product_info, source_dir, logger)
    
    if product_info.get_source == "cvs":
        cvs_user = config.USER.cvs_user
        return get_source_from_cvs(cvs_user, 
                                    product_info, 
                                    source_dir, 
                                    checkout, 
                                    logger,
                                    pad)

    if product_info.get_source == "svn":
        svn_user = config.USER.svn_user
        return get_source_from_svn(svn_user, product_info, source_dir, 
                                    checkout,
                                    logger)

    if product_info.get_source == "native":
        # skip
        logger.write('%s ...' % _("native (ignored)"), 3, False)
        return True        

    if product_info.get_source == "fixed":
        # skip
        logger.write('%s ...' % _("fixed (ignored)"), 3, False)
        return True  
    
    if len(product_info.get_source) == 0:
        # skip
        logger.write('%s ...' % _("ignored"), 3, False)
        return True

    # if the get_source is not in [git, archive, cvs, svn, dir]
    logger.write(_("Unknown get_mehtod %(get)s for product %(product)s") % \
        { 'get': product_info.get_source, 'product': product_info.name }, 3, False)
    logger.write(" ... ", 3, False)
    logger.flush()
    return False

def get_all_product_sources(config, products, force, logger):
    '''Get all the product sources.
    
    :param config Config: The global configuration
    :param products List: The list of tuples (product name, product informations)
    :param force boolean: True if the --force option was invoked
    :param logger Logger: The logger instance to be used for the logging
    :return: the tuple (number of success, dictionary product_name/success_fail)
    :rtype: (int,dict)
    '''

    # Initialize the variables that will count the fails and success
    results = dict()
    good_result = 0

    # Get the maximum name length in order to format the terminal display
    max_product_name_len = 1
    if len(products) > 0:
        max_product_name_len = max(map(lambda l: len(l), products[0])) + 4
    
    # The loop on all the products from which to get the sources
    for product_name, product_info in products:
        # get product name, product informations and the directory where to put
        # the sources
        if not src.product.product_is_fixed(product_info):
            source_dir = src.Path(product_info.source_dir)
        else:
            source_dir = src.Path('')

        # display and log
        logger.write('%s: ' % src.printcolors.printcLabel(product_name), 3)
        logger.write(' ' * (max_product_name_len - len(product_name)), 3, False)
        logger.write("\n", 4, False)
        
        # Remove the existing source directory if 
        # the product is not in development mode
        is_dev = ("dev_products" in config.APPLICATION and 
                  product_name in config.APPLICATION.dev_products)
        if source_dir.exists() and not is_dev:
            logger.write("  " + _('remove %s') % source_dir, 4)
            logger.write("\n  ", 4, False)
            source_dir.rm()

        # Call to the function that get the sources for one product
        retcode = get_product_sources(config, 
                                     product_info, 
                                     is_dev, 
                                     source_dir,
                                     force, 
                                     logger, 
                                     max_product_name_len, 
                                     checkout=False)
        
        '''
        if 'no_rpath' in product_info.keys():
            if product_info.no_rpath:
                hack_no_rpath(config, product_info, logger)
        '''

        # show results
        results[product_name] = retcode
        if retcode == 'N\A':
            # The case where the product was not prepared because it is 
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
    return _("The source command gets the sources of the application products "
             "from cvs, git, an archive or a directory..")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with source parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Print some informations
    logger.write(_('Getting sources of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    src.printcolors.print_value(logger, 'out_dir', 
                                runner.cfg.APPLICATION.out_dir, 2)
    logger.write("\n", 2, False)
    
    # Get the force option if it was passed
    force = options.force
    if force:
        msg = _("Warning: the --force option has effect only "
                "on products in development mode\n\n")
        logger.write(src.printcolors.printcWarning(msg))
    
    # Get the products list with products informations regarding the options
    products_infos = prepare.get_products_list(options, runner.cfg, logger)
    
    # Call to the function that gets all the sources
    good_result, results = get_all_product_sources(runner.cfg, 
                                                  products_infos,
                                                  force,
                                                  logger)

    # Display the results (how much passed, how much failed, etc...)
    status = src.OK_STATUS
    details = []

    logger.write("\n", 2, False)
    if good_result == len(products_infos):
        res_count = "%d / %d" % (good_result, good_result)
    else:
        status = src.KO_STATUS
        res_count = "%d / %d" % (good_result, len(products_infos))

        for product in results:
            if results[product] == 0 or results[product] is None:
                details.append(product)

    result = len(products_infos) - good_result

    # write results
    logger.write(_("Getting sources of the application:"), 1)
    logger.write(" " + src.printcolors.printc(status), 1, False)
    logger.write(" (%s)\n" % res_count, 1, False)

    if len(details) > 0:
        logger.write(_("Following sources haven't been get:\n"), 2)
        logger.write(" ".join(details), 2)
        logger.write("\n", 2, False)

    return result
