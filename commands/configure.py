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

# Define all possible option for configure command :  sat configure <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to configure. This option accepts a comma separated list.'))
parser.add_option('o', 'option', 'string', 'option',
    _('Optional: Option to add to the configure or cmake command.'), "")


def log_step(logger, header, step):
    logger.write("\r%s%s" % (header, " " * 20), 3)
    logger.write("\r%s%s" % (header, step), 3)
    logger.write("\n==== %s \n" % src.printcolors.printcInfo(step), 4)
    logger.flush()

def log_res_step(logger, res):
    if res == 0:
        logger.write("%s \n" % src.printcolors.printcSuccess("OK"), 4)
        logger.flush()
    else:
        logger.write("%s \n" % src.printcolors.printcError("KO"), 4)
        logger.flush()

def configure_all_products(config, products_infos, conf_option, logger):
    '''Execute the proper configuration commands 
       in each product build directory.

    :param config Config: The global configuration
    :param products_info list: List of 
                                 (str, Config) => (product_name, product_info)
    :param conf_option str: The options to add to the command
    :param logger Logger: The logger instance to use for the display and logging
    :return: the number of failing commands.
    :rtype: int
    '''
    res = 0
    for p_name_info in products_infos:
        res_prod = configure_product(p_name_info, conf_option, config, logger)
        if res_prod != 0:
            res += 1 
    return res

def configure_product(p_name_info, conf_option, config, logger):
    '''Execute the proper configuration command(s) 
       in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
    :param conf_option str: The options to add to the command
    :param config Config: The global configuration
    :param logger Logger: The logger instance to use for the display 
                          and logging
    :return: 1 if it fails, else 0.
    :rtype: int
    '''
    
    p_name, p_info = p_name_info
    
    # Logging
    logger.write("\n", 4, False)
    logger.write("################ ", 4)
    header = _("Configuration of %s") % src.printcolors.printcLabel(p_name)
    header += " %s " % ("." * (20 - len(p_name)))
    logger.write(header, 3)
    logger.write("\n", 4, False)
    logger.flush()

    # Do nothing if he product is not compilable
    if ("properties" in p_info and "compilation" in p_info.properties and 
                                        p_info.properties.compilation == "no"):
        log_step(logger, header, "ignored")
        logger.write("\n", 3, False)
        return 0

    # Instantiate the class that manages all the construction commands
    # like cmake, make, make install, make test, environment management, etc...
    builder = src.compilation.Builder(config, logger, p_name, p_info)
    
    # Prepare the environment
    log_step(logger, header, "PREPARE ENV")
    res_prepare = builder.prepare()
    log_res_step(logger, res_prepare)
    
    # Execute buildconfigure, configure if the product is autotools
    # Execute cmake if the product is cmake
    res = 0
    if src.product.product_is_autotools(p_info):
        log_step(logger, header, "BUILDCONFIGURE")
        res_bc = builder.build_configure()
        log_res_step(logger, res_bc)
        res += res_bc
        log_step(logger, header, "CONFIGURE")
        res_c = builder.configure(conf_option)
        log_res_step(logger, res_c)
        res += res_c
    if src.product.product_is_cmake(p_info):
        log_step(logger, header, "CMAKE")
        res_cm = builder.cmake(conf_option)
        log_res_step(logger, res_cm)
        res += res_cm
    
    # Log the result
    if res > 0:
        logger.write("\r%s%s" % (header, " " * 20), 3)
        logger.write("\r" + header + src.printcolors.printcError("KO"))
        logger.write("==== %(KO)s in configuration of %(name)s \n" %
            { "name" : p_name , "KO" : src.printcolors.printcInfo("ERROR")}, 4)
        logger.flush()
    else:
        logger.write("\r%s%s" % (header, " " * 20), 3)
        logger.write("\r" + header + src.printcolors.printcSuccess("OK"))
        logger.write("==== %s \n" % src.printcolors.printcInfo("OK"), 4)
        logger.write("==== Configuration of %(name)s %(OK)s \n" %
            { "name" : p_name , "OK" : src.printcolors.printcInfo("OK")}, 4)
        logger.flush()
    logger.write("\n", 3, False)

    return res

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the configure command description.
    :rtype: str
    '''
    return _("The configure command executes in the build directory"
             " the configure commands corresponding\nto the compilation mode"
             " of the application products.\nThe possible compilation modes"
             " are \"cmake\", \"autotools\", or a script.\n\nHere are the "
             "commands to be run :\nautotools: build_configure and configure\n"
             "cmake: cmake\nscript: do nothing\n\nexample:\nsat configure "
             "SALOME-master --products KERNEL,GUI,PARAVIS")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with make parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Get the list of products to treat
    products_infos = src.product.get_products_list(options, runner.cfg, logger)
    
    # Print some informations
    logger.write(_('Configuring the sources of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    
    info = [(_("BUILD directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'BUILD'))]
    src.print_info(logger, info)
    
    # Call the function that will loop over all the products and execute
    # the right command(s)
    if options.option is None:
        options.option = ""
    res = configure_all_products(runner.cfg, products_infos, options.option, logger)
    
    # Print the final state
    nb_products = len(products_infos)
    if res == 0:
        final_status = "OK"
    else:
        final_status = "KO"
   
    logger.write(_("\nConfiguration: %(status)s (%(valid_result)d/%(nb_products)d)\n") % \
        { 'status': src.printcolors.printc(final_status), 
          'valid_result': nb_products - res,
          'nb_products': nb_products }, 1)    
    
    return res 
