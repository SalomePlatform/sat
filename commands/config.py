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
import platform
import datetime
import shutil
import gettext

import src

# internationalization
satdir  = os.path.dirname(os.path.realpath(__file__))
gettext.install('salomeTools', os.path.join(satdir, 'src', 'i18n'))

# Define all possible option for config command :  sat config <options>
parser = src.options.Options()
parser.add_option('v', 'value', 'string', 'value',
                   _("print the value of CONFIG_VARIABLE."))
parser.add_option('e', 'edit', 'boolean', 'edit',
                   _("edit the product configuration file."))
parser.add_option('l', 'list', 'boolean', 'list',
                  _("list all available applications."))
parser.add_option('c', 'copy', 'boolean', 'copy',
    _("""copy a config file to the personnal config files directory.
\tWARNING the included files are not copied.
\tIf a name is given the new config file takes the given name."""))

class ConfigOpener:
    '''Class that helps to find an application pyconf 
       in all the possible directories (pathList)
    '''
    def __init__(self, pathList):
        '''Initialization
        
        :param pathList list: The list of paths where to serach a pyconf.
        '''
        self.pathList = pathList

    def __call__(self, name):
        if os.path.isabs(name):
            return src.pyconf.ConfigInputStream(open(name, 'rb'))
        else:
            return src.pyconf.ConfigInputStream( 
                        open(os.path.join( self.get_path(name), name ), 'rb') )
        raise IOError(_("Configuration file '%s' not found") % name)

    def get_path( self, name ):
        '''The method that returns the entire path of the pyconf searched
        :param name str: The name of the searched pyconf.
        '''
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
        '''Create a dictionary that stores all information about machine,
           user, date, repositories, etc...
        
        :param application str: The application for which salomeTools is called.
        :param command str: The command that is called.
        :param dataDir str: The repository that contain external data 
                            for salomeTools.
        :return: The dictionary that stores all information.
        :rtype: dict
        '''
        var = {}      
        var['user'] = src.architecture.get_user()
        var['salometoolsway'] = os.path.dirname(
                                    os.path.dirname(os.path.abspath(__file__)))
        var['srcDir'] = os.path.join(var['salometoolsway'], 'src')
        var['sep']= os.path.sep
        
        # dataDir has a default location
        var['dataDir'] = os.path.join(var['salometoolsway'], 'data')
        if dataDir is not None:
            var['dataDir'] = dataDir

        var['personalDir'] = os.path.join(os.path.expanduser('~'),
                                           '.salomeTools')

        # read linux distributions dictionary
        distrib_cfg = src.pyconf.Config(os.path.join(var['srcDir'],
                                                      'internal_config',
                                                      'distrib.pyconf'))
        
        # set platform parameters
        dist_name = src.architecture.get_distribution(
                                            codes=distrib_cfg.DISTRIBUTIONS)
        dist_version = src.architecture.get_distrib_version(dist_name, 
                                                    codes=distrib_cfg.VERSIONS)
        dist = dist_name + dist_version
        
        var['dist_name'] = dist_name
        var['dist_version'] = dist_version
        var['dist'] = dist
        var['python'] = src.architecture.get_python_version()

        var['nb_proc'] = src.architecture.get_nb_proc()
        node_name = platform.node()
        var['node'] = node_name
        var['hostname'] = node_name

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
        if src.architecture.is_windows() : 
            var['tmp_root'] =  os.path.expanduser('~') + os.sep + 'tmp'
        
        return var

    def get_command_line_overrides(self, options, sections):
        '''get all the overwrites that are in the command line
        
        :param options: the options from salomeTools class 
                        initialization (like -l5 or --overwrite)
        :param sections str: The config section to overwrite.
        :return: The list of all the overwrites to apply.
        :rtype: list
        '''
        # when there are no options or not the overwrite option, 
        # return an empty list
        if options is None or options.overwrite is None:
            return []
        
        over = []
        for section in sections:
            # only overwrite the sections that correspond to the option 
            over.extend(filter(lambda l: l.startswith(section + "."), 
                               options.overwrite))
        return over

    def get_config(self, application=None, options=None, command=None,
                    dataDir=None):
        '''get the config from all the configuration files.
        
        :param application str: The application for which salomeTools is called.
        :param options class Options: The general salomeToos
                                      options (--overwrite or -l5, for example)
        :param command str: The command that is called.
        :param dataDir str: The repository that contain 
                            external data for salomeTools.
        :return: The final config.
        :rtype: class 'src.pyconf.Config'
        '''        
        
        # create a ConfigMerger to handle merge
        merger = src.pyconf.ConfigMerger()#MergeHandler())
        
        # create the configuration instance
        cfg = src.pyconf.Config()
        
        # =====================================================================
        # create VARS section
        var = self._create_vars(application=application, command=command, 
                                dataDir=dataDir)
        # add VARS to config
        cfg.VARS = src.pyconf.Mapping(cfg)
        for variable in var:
            cfg.VARS[variable] = var[variable]
        
        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["VARS"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        # =====================================================================
        # Load INTERNAL config
        # read src/internal_config/salomeTools.pyconf
        src.pyconf.streamOpener = ConfigOpener([
                            os.path.join(cfg.VARS.srcDir, 'internal_config')])
        try:
            internal_cfg = src.pyconf.Config(open(os.path.join(cfg.VARS.srcDir, 
                                    'internal_config', 'salomeTools.pyconf')))
        except src.pyconf.ConfigError as e:
            raise src.SatException(_("Error in configuration file:"
                                     " salomeTools.pyconf\n  %(error)s") % \
                                   {'error': str(e) })
        
        merger.merge(cfg, internal_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["INTERNAL"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec        
        
        # =====================================================================
        # Load SITE config file
        # search only in the data directory
        src.pyconf.streamOpener = ConfigOpener([cfg.VARS.dataDir])
        try:
            site_cfg = src.pyconf.Config(open(os.path.join(cfg.VARS.dataDir, 
                                                           'site.pyconf')))
        except src.pyconf.ConfigError as e:
            raise src.SatException(_("Error in configuration file: "
                                     "site.pyconf\n  %(error)s") % \
                {'error': str(e) })
        except IOError as error:
            e = str(error)
            if "site.pyconf" in e :
                e += ("\nYou can copy data"
                  + cfg.VARS.sep
                  + "site.template.pyconf to data"
                  + cfg.VARS.sep 
                  + "site.pyconf and edit the file")
            raise src.SatException( e );
        
        # add user local path for configPath
        site_cfg.SITE.config.configPath.append(
                        os.path.join(cfg.VARS.personalDir, 'Applications'), 
                        "User applications path")
        
        merger.merge(cfg, site_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["SITE"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
  
        
        # =====================================================================
        # Load APPLICATION config file
        if application is not None:
            # search APPLICATION file in all directories in configPath
            cp = cfg.SITE.config.configPath
            src.pyconf.streamOpener = ConfigOpener(cp)
            try:
                application_cfg = src.pyconf.Config(application + '.pyconf')
            except IOError as e:
                raise src.SatException(_("%s, use 'config --list' to get the"
                                         " list of available applications.") %e)
            except src.pyconf.ConfigError as e:
                raise src.SatException(_("Error in configuration file:"
                                " %(application)s.pyconf\n  %(error)s") % \
                    { 'application': application, 'error': str(e) } )

            merger.merge(cfg, application_cfg)

            # apply overwrite from command line if needed
            for rule in self.get_command_line_overrides(options,
                                                         ["APPLICATION"]):
                # this cannot be factorized because of the exec
                exec('cfg.' + rule) 
        
        # =====================================================================
        # Load softwares config files in SOFTWARE section
       
        # The directory containing the softwares definition
        softsDir = os.path.join(cfg.VARS.dataDir, 'softwares')
        
        # Loop on all files that are in softsDir directory 
        # and read their config
        for fName in os.listdir(softsDir):
            if fName.endswith(".pyconf"):
                src.pyconf.streamOpener = ConfigOpener([softsDir])
                try:
                    soft_cfg = src.pyconf.Config(open(
                                                os.path.join(softsDir, fName)))
                except src.pyconf.ConfigError as e:
                    raise src.SatException(_(
                        "Error in configuration file: %(soft)s\n  %(error)s") % \
                        {'soft' :  fName, 'error': str(e) })
                except IOError as error:
                    e = str(error)
                    raise src.SatException( e );
                
                merger.merge(cfg, soft_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["SOFTWARE"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec

        
        # =====================================================================
        # load USER config
        self.set_user_config_file(cfg)
        user_cfg_file = self.get_user_config_file()
        user_cfg = src.pyconf.Config(open(user_cfg_file))
        merger.merge(cfg, user_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["USER"]):
            exec('cfg.' + rule) # this cannot be factorize because of the exec

        return cfg

    def set_user_config_file(self, config):
        '''Set the user config file name and path.
        If necessary, build it from another one or create it from scratch.
        
        :param config class 'src.pyconf.Config': The global config 
                                                 (containing all pyconf).
        '''
        # get the expected name and path of the file
        self.config_file_name = 'salomeTools.pyconf'
        self.user_config_file_path = os.path.join(config.VARS.personalDir,
                                                   self.config_file_name)
        
        # if pyconf does not exist, create it from scratch
        if not os.path.isfile(self.user_config_file_path): 
            self.create_config_file(config)
    
    def create_config_file(self, config):
        '''This method is called when there are no user config file. 
           It build it from scratch.
        
        :param config class 'src.pyconf.Config': The global config.
        :return: the config corresponding to the file created.
        :rtype: config class 'src.pyconf.Config'
        '''
        
        cfg_name = self.get_user_config_file()

        user_cfg = src.pyconf.Config()
        #
        user_cfg.addMapping('USER', src.pyconf.Mapping(user_cfg), "")

        #
        user_cfg.USER.addMapping('workDir', os.path.expanduser('~'),
            "This is where salomeTools will work. "
            "You may (and probably do) change it.\n")
        user_cfg.USER.addMapping('cvs_user', config.VARS.user,
            "This is the user name used to access salome cvs base.\n")
        user_cfg.USER.addMapping('svn_user', config.VARS.user,
            "This is the user name used to access salome svn base.\n")
        user_cfg.USER.addMapping('output_level', 3,
            "This is the default output_level you want."
            " 0=>no output, 5=>debug.\n")
        user_cfg.USER.addMapping('publish_dir', 
                                 os.path.join(os.path.expanduser('~'),
                                 'websupport', 
                                 'satreport'), 
                                 "")
        user_cfg.USER.addMapping('editor',
                                 'vi', 
                                 "This is the editor used to "
                                 "modify configuration files\n")
        user_cfg.USER.addMapping('browser', 
                                 'firefox', 
                                 "This is the browser used to "
                                 "read html documentation\n")
        user_cfg.USER.addMapping('pdf_viewer', 
                                 'evince', 
                                 "This is the pdf_viewer used "
                                 "to read pdf documentation\n")
        # 
        src.ensure_path_exists(config.VARS.personalDir)
        src.ensure_path_exists(os.path.join(config.VARS.personalDir, 
                                            'Applications'))

        f = open(cfg_name, 'w')
        user_cfg.__save__(f)
        f.close()
        print(_("You can edit it to configure salomeTools "
                "(use: sat config --edit).\n"))

        return user_cfg   

    def get_user_config_file(self):
        '''Get the user config file
        :return: path to the user config file.
        :rtype: str
        '''
        if not self.user_config_file_path:
            raise src.SatException(_("Error in get_user_config_file: "
                                     "missing user config file path"))
        return self.user_config_file_path     
        
    
def print_value(config, path, show_label, logger, level=0, show_full_path=False):
    '''Prints a value from the configuration. Prints recursively the values 
       under the initial path.
    
    :param config class 'src.pyconf.Config': The configuration 
                                             from which the value is displayed.
    :param path str : the path in the configuration of the value to print.
    :param show_label boolean: if True, do a basic display. 
                               (useful for bash completion)
    :param logger Logger: the logger instance
    :param level int: The number of spaces to add before display.
    :param show_full_path :
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
        logger.write(tab_level)
        logger.write("%s: ERROR %s\n" % (src.printcolors.printcLabel(vname), 
                                         src.printcolors.printcError(str(e))))
        return

    # in this case, display only the value
    if show_label:
        logger.write(tab_level)
        logger.write("%s: " % src.printcolors.printcLabel(vname))

    # The case where the value has under values, 
    # do a recursive call to the function
    if dir(val).__contains__('keys'):
        if show_label: logger.write("\n")
        for v in sorted(val.keys()):
            print_value(config, path + '.' + v, show_label, logger, level + 1)
    elif val.__class__ == src.pyconf.Sequence or isinstance(val, list): 
        # in this case, value is a list (or a Sequence)
        if show_label: logger.write("\n")
        index = 0
        for v in val:
            print_value(config, path + "[" + str(index) + "]", 
                        show_label, logger, level + 1)
            index = index + 1
    else: # case where val is just a str
        logger.write("%s\n" % val)

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the config command description.
    :rtype: str
    '''
    return _("The config command allows manipulation "
             "and operation on config files.")
    

def run(args, runner, logger):
    '''method that is called when salomeTools is called with config parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)
    
    # case : print a value of the config
    if options.value:
        if options.value == ".":
            # if argument is ".", print all the config
            for val in sorted(runner.cfg.keys()):
                print_value(runner.cfg, val, True, logger)
        else:
            print_value(runner.cfg, options.value, True, logger, 
                        level=0, show_full_path=False)
    
    # case : edit user pyconf file or application file
    elif options.edit:
        editor = runner.cfg.USER.editor
        if 'APPLICATION' not in runner.cfg: # edit user pyconf
            usercfg = os.path.join(runner.cfg.VARS.personalDir, 
                                   'salomeTools.pyconf')
            src.system.show_in_editor(editor, usercfg, logger)
        else:
            # search for file <application>.pyconf and open it
            for path in runner.cfg.SITE.config.configPath:
                pyconf_path = os.path.join(path, 
                                    runner.cfg.VARS.application + ".pyconf")
                if os.path.exists(pyconf_path):
                    src.system.show_in_editor(editor, pyconf_path, logger)
                    break
    
    # case : copy an existing <application>.pyconf 
    # to ~/.salomeTools/Applications/LOCAL_<application>.pyconf
    elif options.copy:
        # product is required
        src.check_config_has_application( runner.cfg )

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
            raise src.SatException(_(
                        "Config file for product %s not found\n") % source)
        else:
            if len(args) > 0:
                # a name is given as parameter, use it
                dest = args[0]
            elif 'copy_prefix' in runner.cfg.SITE.config:
                # use prefix
                dest = (runner.cfg.SITE.config.copy_prefix 
                        + runner.cfg.VARS.application)
            else:
                # use same name as source
                dest = runner.cfg.VARS.application
                
            # the full path
            dest_file = os.path.join(runner.cfg.VARS.personalDir, 
                                     'Applications', dest + '.pyconf')
            if os.path.exists(dest_file):
                raise src.SatException(_("A personal application"
                                         " '%s' already exists") % dest)
            
            # perform the copy
            shutil.copyfile(source_full_path, dest_file)
            logger.write(_("%s has been created.\n") % dest_file)
    
    # case : display all the available pyconf applications
    elif options.list:
        lproduct = list()
        # search in all directories that can have pyconf applications
        for path in runner.cfg.SITE.config.configPath:
            # print a header
            logger.write("------ %s\n" % src.printcolors.printcHeader(path))

            if not os.path.exists(path):
                logger.write(src.printcolors.printcError(_(
                                            "Directory not found")) + "\n")
            else:
                for f in sorted(os.listdir(path)):
                    # ignore file that does not ends with .pyconf
                    if not f.endswith('.pyconf'):
                        continue

                    appliname = f[:-len('.pyconf')]
                    if appliname not in lproduct:
                        lproduct.append(appliname)
                        if path.startswith(runner.cfg.VARS.personalDir):
                            logger.write("%s*\n" % appliname)
                        else:
                            logger.write("%s\n" % appliname)
                            
            logger.write("\n")
    
    