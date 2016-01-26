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
import sys
import common
import platform
import datetime

# Define all possible option for config command :  sat config <options>
parser = common.options.Options()
parser.add_option('v', 'value', 'string', 'value', "print the value of CONFIG_VARIABLE.")

'''
class MergeHandler:
    def __init__(self):
        pass

    def __call__(self, map1, map2, key):
        if '__overwrite__' in map2 and key in map2.__overwrite__:
            return "overwrite"
        else:
            return common.config_pyconf.overwriteMergeResolve(map1, map2, key)
'''

class ConfigManager:
    '''Class that manages the read of all the configuration files of salomeTools
    '''
    def __init__(self, dataDir=None):
        pass

    def _create_vars(self, application=None, command=None, dataDir=None):
        '''Create a dictionary that stores all information about machine, user, date, repositories, etc...
        :param application str: The application for which salomeTools is called.
        :param command str: The command that is called.
        :param dataDir str: The repository that contain external data for salomeTools.
        :return: The dictionary that stores all information.
        :rtype: dict
        '''
        var = {}      
        var['user'] = common.architecture.get_user()
        var['salometoolsway'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        var['srcDir'] = os.path.join(var['salometoolsway'], 'src')
        var['sep']= os.path.sep
        
        # dataDir has a default location
        var['dataDir'] = os.path.join(var['salometoolsway'], 'data')
        if dataDir is not None:
            var['dataDir'] = dataDir

        var['personalDir'] = os.path.join(os.path.expanduser('~'), '.salomeTools')

        # read linux distributions dictionary
        distrib_cfg = common.config_pyconf.Config(os.path.join(var['dataDir'], "distrib.pyconf"))

        # set platform parameters
        dist_name = common.architecture.get_distribution(codes=distrib_cfg.DISTRIBUTIONS)
        dist_version = common.architecture.get_distrib_version(dist_name, codes=distrib_cfg.VERSIONS)
        dist = dist_name + dist_version
        
        # Forcing architecture with env variable ARCH on Windows
        if common.architecture.is_windows() and "ARCH" in os.environ :
            bitsdict={"Win32":"32","Win64":"64"}
            nb_bits = bitsdict[os.environ["ARCH"]]
        else :
            nb_bits = common.architecture.get_nb_bit()

        var['dist_name'] = dist_name
        var['dist_version'] = dist_version
        var['dist'] = dist
        var['arch'] = dist + '_' + nb_bits
        var['bits'] = nb_bits
        var['python'] = common.architecture.get_python_version()

        var['nb_proc'] = common.architecture.get_nb_proc()
        node_name = platform.node()
        var['node'] = node_name
        var['hostname'] = node_name
        # particular win case 
        if common.architecture.is_windows() :
            var['hostname'] = node_name+'-'+nb_bits

        # set date parameters
        dt = datetime.datetime.now()
        var['date'] = dt.strftime('%Y%m%d')
        var['datehour'] = dt.strftime('%Y%m%d_%H%M%S')
        var['hour'] = dt.strftime('%H%M%S')

        var['command'] = str(command)
        var['application'] = str(application)

        # Root dir for temporary files 
        var['tmp_root'] = os.sep + 'tmp' + os.sep + var['user']
        # particular win case 
        if common.architecture.is_windows() : 
            var['tmp_root'] =  os.path.expanduser('~') + os.sep + 'tmp'
        
        return var

    def get_command_line_overrides(self, options, sections):
        '''get all the overwrites that are in the command line
        :param options : TO DO
        :param sections str: The command that is called.
        :return: The list of all the overwrites of the command line.
        :rtype: list
        '''
        # when there are no options or not the overwrite option, return an empty list
        if options is None or options.overwrite is None:
            return []

        over = []
        for section in sections:
            over.extend(filter(lambda l: l.startswith(section + "."), options.overwrite))
        return over

    def getConfig(self, application=None, options=None, command=None, dataDir=None):
        '''get the config from all the configuration files.
        :param application str: The application for which salomeTools is called.
        :param options TODO
        :param command str: The command that is called.
        :param dataDir str: The repository that contain external data for salomeTools.
        :return: The final config.
        :rtype: class 'common.config_pyconf.Config'
        '''        
        
        # create a ConfigMerger to handle merge
        merger = common.config_pyconf.ConfigMerger()#MergeHandler())
        
        # create the configuration instance
        cfg = common.config_pyconf.Config()
        
        # =======================================================================================
        # create VARS section
        var = self._create_vars(application=application, command=command, dataDir=dataDir)
        # add VARS to config
        cfg.VARS = common.config_pyconf.Mapping(cfg)
        for variable in var:
            cfg.VARS[variable] = var[variable]

        for rule in self.get_command_line_overrides(options, ["VARS"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        return cfg
    
    
def print_value(config, path, show_label, level=0, show_full_path=False):
    '''Prints a value from the configuration. Prints recursively the values under the initial path.
    :param config class 'common.config_pyconf.Config': The configuration from which the value is displayed.
    :param path str : the path in the configuration of the value to print.
    :param show_label boolean: if True, do a basic display. (useful for bash completion)
    :param level int: The number of spaces to add before display.
    :param show_full_path :
    :return: The final config.
    :rtype: class 'common.config_pyconf.Config'
    '''            
    
    # display all the path or not
    if show_full_path:
        vname = path
    else:
        vname = path.split('.')[-1]

    # number of spaces before the display
    tab_level = "  " * level
    
    # call to the function that gets the value of the path.
    try:
        val = config.getByPath(path)
    except Exception as e:
        sys.stdout.write(tab_level)
        sys.stdout.write("%s: ERROR %s\n" % (common.printcolors.printcLabel(vname), common.printcolors.printcError(str(e))))
        return

    # in this case, display only the value
    if show_label:
        sys.stdout.write(tab_level)
        sys.stdout.write("%s: " % common.printcolors.printcLabel(vname))

    # The case where the value has under values, do a recursive call to the function
    if dir(val).__contains__('keys'):
        if show_label: sys.stdout.write("\n")
        for v in sorted(val.keys()):
            print_value(config, path + '.' + v, show_label, level + 1)
    elif val.__class__ == common.config_pyconf.Sequence or isinstance(val, list): # in this case, value is a list (or a Sequence)
        if show_label: sys.stdout.write("\n")
        index = 0
        for v in val:
            print_value(config, path + "[" + str(index) + "]", show_label, level + 1)
            index = index + 1
    else: # case where val is just a str
        sys.stdout.write("%s\n" % val)
        
def run(args, runner):
    (options, args) = parser.parse_args(args)
    print('Je suis dans la commande config ! Bien joué ! COUCOU')
    if options.value:
        print_value(runner.cfg, options.value, True, level=0, show_full_path=False)
    
    runner.config_copy('-v VARS')