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

# Define all possible option for the check command :  sat check <options>
parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    _('Optional: products to check. This option accepts a comma separated list.'))

CHECK_PROPERTY = "has_unit_tests"


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

def check_all_products(config, products_infos, logger):
    '''Execute the proper configuration commands 
       in each product build directory.

    :param config Config: The global configuration
    :param products_info list: List of 
                                 (str, Config) => (product_name, product_info)
    :param logger Logger: The logger instance to use for the display and logging
    :return: the number of failing commands.
    :rtype: int
    '''
    res = 0
    for p_name_info in products_infos:
        res_prod = check_product(p_name_info, config, logger)
        if res_prod != 0:
            res += 1 
    return res

def check_product(p_name_info, config, logger):
    '''Execute the proper configuration command(s) 
       in the product build directory.
    
    :param p_name_info tuple: (str, Config) => (product_name, product_info)
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
    header = _("Check of %s") % src.printcolors.printcLabel(p_name)
    header += " %s " % ("." * (20 - len(p_name)))
    logger.write(header, 3)
    logger.write("\n", 4, False)
    logger.flush()

    # Verify if the command has to be launched or not
    ignored = False
    if src.product.product_is_native(p_info):
        msg = _("The product %s is defined as being native. "
                "product ignored." % p_name)
        logger.write("%s\n" % msg, 4)
        ignored = True
    elif not src.get_property_in_product_cfg(p_info, CHECK_PROPERTY):
        msg = _("The product %s is defined as not having tests. "
                "product ignored." % p_name)
        logger.write("%s\n" % msg, 4)
        ignored = True
    elif not src.product.product_compiles(p_info):
        msg = _("The product %s is defined as not compiling. "
                "product ignored." % p_name)
        logger.write("%s\n" % msg, 4)
        ignored = True
    elif "build_dir" not in p_info:
        msg = _("No build_dir key defined in "
                "the config file of %s: product ignored." % p_name)
        logger.write("%s\n" % msg, 4)
        ignored = True


    # Get the command to execute for script products
    cmd_found = True
    command = ""
    if src.product.product_has_script(p_info) and not ignored:
        command = src.get_cfg_param(p_info, "test_build", "Not found")
        if command == "Not found":
            cmd_found = False
            msg = _('WARNING: The product %s is defined as having tests. But it'
                    ' is compiled using a script and the key "test_build" is '
                    'not defined in the definition of %s' % (p_name, p_name))
            logger.write("%s\n" % msg, 4)
                
    if ignored or not cmd_found:
        log_step(logger, header, "ignored")
        logger.write("==== %(name)s %(IGNORED)s\n" %
            { "name" : p_name ,
             "IGNORED" : src.printcolors.printcInfo("IGNORED")},
            4)
        logger.write("\n", 3, False)
        logger.flush()
        if not cmd_found:
            return 1
        return 0
    
    # Instantiate the class that manages all the construction commands
    # like cmake, check, make install, make test, environment management, etc...
    builder = src.compilation.Builder(config, logger, p_name, p_info)
    
    # Prepare the environment
    log_step(logger, header, "PREPARE ENV")
    res_prepare = builder.prepare(add_env_launch=True)
    log_res_step(logger, res_prepare)
    
    len_end_line = 20

    # Launch the check    
    log_step(logger, header, "CHECK")
    res = builder.check(command=command)
    log_res_step(logger, res)
    
    # Log the result
    if res > 0:
        logger.write("\r%s%s" % (header, " " * len_end_line), 3)
        logger.write("\r" + header + src.printcolors.printcError("KO"))
        logger.write("==== %(KO)s in check of %(name)s \n" %
            { "name" : p_name , "KO" : src.printcolors.printcInfo("ERROR")}, 4)
        logger.flush()
    else:
        logger.write("\r%s%s" % (header, " " * len_end_line), 3)
        logger.write("\r" + header + src.printcolors.printcSuccess("OK"))
        logger.write("==== %s \n" % src.printcolors.printcInfo("OK"), 4)
        logger.write("==== Check of %(name)s %(OK)s \n" %
            { "name" : p_name , "OK" : src.printcolors.printcInfo("OK")}, 4)
        logger.flush()
    logger.write("\n", 3, False)

    return res

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the check command description.
    :rtype: str
    '''
    return _("The check command executes the \"check\" command in"
             " the build directory of all the products of the application."
             "\nIt is possible to reduce the list of products to check by using"
             " the --products option\n\nexample\nsat check SALOME-master "
             "--products KERNEL,GUI,GEOM")
  
def run(args, runner, logger):
    '''method that is called when salomeTools is called with check parameter.
    '''
    
    # Parse the options
    (options, args) = parser.parse_args(args)

    # check that the command has been called with an application
    src.check_config_has_application( runner.cfg )

    # Get the list of products to treat
    products_infos = src.product.get_products_list(options, runner.cfg, logger)
    
    # Print some informations
    logger.write(_('Executing the check command in the build '
                                'directories of the application %s\n') % 
                src.printcolors.printcLabel(runner.cfg.VARS.application), 1)
    
    info = [(_("BUILD directory"),
             os.path.join(runner.cfg.APPLICATION.workdir, 'BUILD'))]
    src.print_info(logger, info)
    
    # Call the function that will loop over all the products and execute
    # the right command(s)
    res = check_all_products(runner.cfg, products_infos, logger)
    
    # Print the final state
    nb_products = len(products_infos)
    if res == 0:
        final_status = "OK"
    else:
        final_status = "KO"
   
    logger.write(_("\nCheck: %(status)s (%(valid_result)d/%(nb_products)d)\n") % \
        { 'status': src.printcolors.printc(final_status), 
          'valid_result': nb_products - res,
          'nb_products': nb_products }, 1)    
    
    return res 
