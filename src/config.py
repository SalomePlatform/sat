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
import platform
import datetime
import glob
import re
import shutil
import gettext

import common

# internationalization
srcdir = os.path.dirname(os.path.realpath(__file__))
gettext.install('salomeTools', os.path.join(srcdir, 'common', 'i18n'))

# Define all possible option for config command :  sat config <options>
parser = common.options.Options()
parser.add_option('v', 'value', 'string', 'value', _("print the value of CONFIG_VARIABLE."))
parser.add_option('e', 'edit', 'boolean', 'edit', _("edit the product configuration file."))
parser.add_option('l', 'list', 'boolean', 'list',_("list all available applications."))
parser.add_option('c', 'copy', 'boolean', 'copy',
    _("""copy a config file to the personnal config files directory.
\tWARNING the included files are not copied.
\tIf a name is given the new config file takes the given name."""))

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

class ConfigOpener:
    def __init__(self, pathList):
        self.pathList = pathList

    def __call__(self, name):
        if os.path.isabs(name):
            return common.config_pyconf.ConfigInputStream(open(name, 'rb'))
        else:
            return common.config_pyconf.ConfigInputStream( open(os.path.join( self.getPath(name), name ), 'rb') )
        raise IOError(_("Configuration file '%s' not found") % name)

    def getPath( self, name ):
        for path in self.pathList:
            if os.path.exists(os.path.join(path, name)):
                return path
        raise IOError(_("Configuration file '%s' not found") % name)

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
        :param options : the options from salomeTools class initialization (like -l5 or --overwrite)
        :param sections str: The config section to overwrite.
        :return: The list of all the overwrites to apply.
        :rtype: list
        '''
        # when there are no options or not the overwrite option, return an empty list
        if options is None or options.overwrite is None:
            return []
        
        over = []
        for section in sections:
            # only overwrite the sections that correspond to the option 
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
        
        # =======================================================================================
        # Load INTERNAL config
        # read src/common/internal_config/salomeTools.pyconf
        common.config_pyconf.streamOpener = ConfigOpener([os.path.join(cfg.VARS.srcDir, 'common', 'internal_config')])
        try:
            internal_cfg = common.config_pyconf.Config(open(os.path.join(cfg.VARS.srcDir, 'common', 'internal_config', 'salomeTools.pyconf')))
        except common.config_pyconf.ConfigError as e:
            raise common.SatException(_("Error in configuration file: salomeTools.pyconf\n  %(error)s") % \
                {'error': str(e) })

        merger.merge(cfg, internal_cfg)

        for rule in self.get_command_line_overrides(options, ["INTERNAL"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec        
        
        # =======================================================================================
        # Load SITE config file
        # search only in the data directory
        common.config_pyconf.streamOpener = ConfigOpener([cfg.VARS.dataDir])
        try:
            site_cfg = common.config_pyconf.Config(open(os.path.join(cfg.VARS.dataDir, 'site.pyconf')))
        except common.config_pyconf.ConfigError as e:
            raise common.SatException(_("Error in configuration file: site.pyconf\n  %(error)s") % \
                {'error': str(e) })
        except IOError as error:
            e = str(error)
            if "site.pyconf" in e :
                e += "\nYou can copy data" + cfg.VARS.sep + "site.template.pyconf to data" + cfg.VARS.sep + "site.pyconf and edit the file"
            raise common.SatException( e );
        
        # add user local path for configPath
        site_cfg.SITE.config.configPath.append(os.path.join(cfg.VARS.personalDir, 'Applications'), "User applications path")
        
        merger.merge(cfg, site_cfg)

        for rule in self.get_command_line_overrides(options, ["SITE"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        # =======================================================================================
        # Load APPLICATION config file
        if application is not None:
            # search APPLICATION file in all directories in configPath
            cp = cfg.SITE.config.configPath
            common.config_pyconf.streamOpener = ConfigOpener(cp)
            try:
                application_cfg = common.config_pyconf.Config(application + '.pyconf')
            except IOError as e:
                raise common.SatException(_("%s, use 'config --list' to get the list of available applications.") %e)
            except common.config_pyconf.ConfigError as e:
                raise common.SatException(_("Error in configuration file: %(application)s.pyconf\n  %(error)s") % \
                    { 'application': application, 'error': str(e) } )

            merger.merge(cfg, application_cfg)

            for rule in self.get_command_line_overrides(options, ["APPLICATION"]):
                exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        # =======================================================================================
        # load USER config
        self.setUserConfigFile(cfg)
        user_cfg_file = self.getUserConfigFile()
        user_cfg = common.config_pyconf.Config(open(user_cfg_file))
        merger.merge(cfg, user_cfg)

        for rule in self.get_command_line_overrides(options, ["USER"]):
            exec('cfg.' + rule) # this cannot be factorize because of the exec

        return cfg

    def setUserConfigFile(self, config):
        '''Set the user config file name and path.
        If necessary, build it from another one or create it from scratch.
        '''
        if not config:
            raise common.SatException(_("Error in setUserConfigFile: config is None"))
        sat_version = config.INTERNAL.sat_version
        self.config_file_name = 'salomeTools-%s.pyconf'%sat_version
        self.user_config_file_path = os.path.join(config.VARS.personalDir, self.config_file_name)
        if not os.path.isfile(self.user_config_file_path):
            # if pyconf does not exist, 
            # Make a copy of an existing  salomeTools-<sat_version>.pyconf
            # or at least a copy of salomeTools.pyconf
            # If there is no pyconf file at all, create it from scratch 
            already_exisiting_pyconf_file = self.getAlreadyExistingUserPyconf( config.VARS.personalDir, sat_version )
            if already_exisiting_pyconf_file:  
                # copy
                shutil.copyfile( already_exisiting_pyconf_file, self.user_config_file_path )
            else: # create from scratch
                self.createConfigFile(config)
    
    def getAlreadyExistingUserPyconf(self, userDir, sat_version ):
        '''Get a pyconf file younger than the given sat version in the given directory
        The file basename can be one of salometools-<younger version>.pyconf or salomeTools.pyconf
        Returns the file path or None if no file has been found.
        '''
        file_path = None  
        # Get a younger pyconf version   
        pyconfFiles = glob.glob( os.path.join(userDir, 'salomeTools-*.pyconf') )
        sExpr = "^salomeTools-(.*)\.pyconf$"
        oExpr = re.compile(sExpr)
        younger_version = None
        for s in pyconfFiles:
            oSreMatch = oExpr.search( os.path.basename(s) )
            if oSreMatch:
                pyconf_version = oSreMatch.group(1)
                if pyconf_version < sat_version: 
                    younger_version = pyconf_version 

        # Build the pyconf filepath
        if younger_version :   
            file_path = os.path.join( userDir, 'salomeTools-%s.pyconf'%younger_version )
        elif os.path.isfile( os.path.join(userDir, 'salomeTools.pyconf') ):
            file_path = os.path.join( userDir, 'salomeTools.pyconf' )
        
        return file_path 
    
    def createConfigFile(self, config):
        
        cfg_name = self.getUserConfigFile()

        user_cfg = common.config_pyconf.Config()
        #
        user_cfg.addMapping('USER', common.config_pyconf.Mapping(user_cfg), "")

        #
        user_cfg.USER.addMapping('workDir', os.path.expanduser('~'),
            "This is where salomeTools will work. You may (and probably do) change it.\n")
        user_cfg.USER.addMapping('cvs_user', config.VARS.user,
            "This is the user name used to access salome cvs base.\n")
        user_cfg.USER.addMapping('svn_user', config.VARS.user,
            "This is the user name used to access salome svn base.\n")
        user_cfg.USER.addMapping('output_level', 3,
            "This is the default output_level you want. 0=>no output, 5=>debug.\n")
        user_cfg.USER.addMapping('publish_dir', os.path.join(os.path.expanduser('~'), 'websupport', 'satreport'), "")
        user_cfg.USER.addMapping('editor', 'vi', "This is the editor used to modify configuration files\n")
        user_cfg.USER.addMapping('browser', 'firefox', "This is the browser used to read html documentation\n")
        user_cfg.USER.addMapping('pdf_viewer', 'evince', "This is the pdf_viewer used to read pdf documentation\n")
        # 
        common.ensure_path_exists(config.VARS.personalDir)
        common.ensure_path_exists(os.path.join(config.VARS.personalDir, 'Applications'))

        f = open(cfg_name, 'w')
        user_cfg.__save__(f)
        f.close()
        print(_("You can edit it to configure salomeTools (use: sat config --edit).\n"))

        return user_cfg   

    def getUserConfigFile(self):
        '''Get the user config file
        '''
        if not self.user_config_file_path:
            raise common.SatException(_("Error in getUserConfigFile: missing user config file path"))
        return self.user_config_file_path     
        
    
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

def description():
    return _("The config command allows manipulation and operation on config files.")
    

def run(args, runner):
    (options, args) = parser.parse_args(args)
    
    # case : print a value of the config
    if options.value:
        if options.value == ".":
            # if argument is ".", print all the config
            for val in sorted(runner.cfg.keys()):
                print_value(runner.cfg, val, True)
            return
        print_value(runner.cfg, options.value, True, level=0, show_full_path=False)
        return
    
    # case : edit user pyconf file or application file
    elif options.edit:
        editor = runner.cfg.USER.editor
        if 'APPLICATION' not in runner.cfg: # edit user pyconf
            usercfg = os.path.join(runner.cfg.VARS.personalDir, 'salomeTools-%s.pyconf'%runner.cfg.INTERNAL['sat_version'])
            common.fileSystem.show_in_editor(editor, usercfg)
        else:
            # search for file <application>.pyconf and open it
            for path in runner.cfg.SITE.config.configPath:
                pyconf_path = os.path.join(path, runner.cfg.VARS.application + ".pyconf")
                if os.path.exists(pyconf_path):
                    common.fileSystem.show_in_editor(editor, pyconf_path)
                    break
    
    # case : copy an existing <application>.pyconf to ~/.salomeTools/Applications/LOCAL_<application>.pyconf
    elif options.copy:
        # product is required
        common.check_config_has_application( runner.cfg )

        # get application file path 
        source = runner.cfg.VARS.application + '.pyconf'
        source_full_path = ""
        for path in runner.cfg.SITE.config.configPath:
            # ignore personal directory
            if path == runner.cfg.VARS.personalDir:
                continue
            # loop on all directories that can have pyconf applications
            zz = os.path.join(path, source)
            if os.path.exists(zz):
                source_full_path = zz
                break

        if len(source_full_path) == 0:
            raise common.SatException(_("Config file for product %s not found\n") % source)
        else:
            if len(args) > 0:
                # a name is given as parameter, use it
                dest = args[0]
            elif 'copy_prefix' in runner.cfg.SITE.config:
                # use prefix
                dest = runner.cfg.SITE.config.copy_prefix + runner.cfg.VARS.application
            else:
                # use same name as source
                dest = runner.cfg.VARS.application
                
            # the full path
            dest_file = os.path.join(runner.cfg.VARS.personalDir, 'Applications', dest + '.pyconf')
            if os.path.exists(dest_file):
                raise common.SatException(_("A personal application '%s' already exists") % dest)
            
            # perform the copy
            shutil.copyfile(source_full_path, dest_file)
            print(_("%s has been created.") % dest_file)
    
    # case : display all the available pyconf applications
    elif options.list:
        lproduct = list()
        # search in all directories that can have pyconf applications
        for path in runner.cfg.SITE.config.configPath:
            # print a header
            sys.stdout.write("------ %s\n" % common.printcolors.printcHeader(path))

            if not os.path.exists(path):
                sys.stdout.write(common.printcolors.printcError(_("Directory not found")) + "\n")
            else:
                for f in sorted(os.listdir(path)):
                    # ignore file that does not ends with .pyconf
                    if not f.endswith('.pyconf'):
                        continue

                    appliname = f[:-len('.pyconf')]
                    if appliname not in lproduct:
                        lproduct.append(appliname)
                        if path.startswith(runner.cfg.VARS.personalDir):
                            sys.stdout.write("%s*\n" % appliname)
                        else:
                            sys.stdout.write("%s\n" % appliname)

            sys.stdout.write("\n")
    
    