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
import shutil
import gettext
import pprint as PP

import src
import src.logger as LOG
import src.debug as DBG
import src.callerName as CALN

logger = LOG.getDefaultLogger()

verbose = False # True for debug

# internationalization
satdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
gettext.install('salomeTools', os.path.join(satdir, 'src', 'i18n'))

# Define all possible option for config command :  sat config <options>
parser = src.options.Options()
parser.add_option('v', 'value', 'string', 'value',
    _("Optional: print the value of CONFIG_VARIABLE."))
parser.add_option('g', 'debug', 'string', 'debug',
    _("Optional: print the debugging mode value of CONFIG_VARIABLE."))
parser.add_option('e', 'edit', 'boolean', 'edit',
    _("Optional: edit the product configuration file."))
parser.add_option('i', 'info', 'list2', 'info',
    _("Optional: get information on product(s). This option accepts a comma separated list."))
parser.add_option('p', 'products', 'list2', 'products',
    _("Optional: same as --info, for convenience."))
parser.add_option('l', 'list', 'boolean', 'list',
    _("Optional: list all available applications."))
parser.add_option('', 'show_patchs', 'boolean', 'show_patchs',
    _("Optional: synthetic list of all patches used in the application"))
parser.add_option('', 'show_dependencies', 'boolean', 'show_dependencies',
    _("Optional: list of product dependencies in the application"))
parser.add_option('', 'show_install', 'boolean', 'show_install',
    _("Optional: synthetic list of all install directories in the application"))
parser.add_option('', 'show_properties', 'boolean', 'show_properties',
    _("Optional: synthetic list of all properties used in the application"))
parser.add_option('', 'check_system', 'boolean', 'check_system',
    _("Optional: check if system products are installed"))
parser.add_option('c', 'copy', 'boolean', 'copy',
    _("""Optional: copy a config file to the personal config files directory.
WARNING: the included files are not copied.
If a name is given the new config file takes the given name."""))
parser.add_option('n', 'no_label', 'boolean', 'no_label',
    _("Internal use: do not print labels, Works only with --value and --list."))
parser.add_option('', 'completion', 'boolean', 'completion',
    _("Internal use: print only keys, works only with --value."))
parser.add_option('s', 'schema', 'boolean', 'schema',
    _("Internal use."))

def osJoin(*args):
  """
  shortcut wrapper to os.path.join
  plus optionaly print for debug
  """
  res = os.path.realpath(os.path.join(*args))
  if verbose:
    if True: # ".pyconf" in res:
      logger.info("osJoin %-80s in %s" % (res, CALN.caller_name(1)))
  return res

class ConfigOpener:
    '''Class that helps to find an application pyconf 
       in all the possible directories (pathList)
    '''
    def __init__(self, pathList):
        '''Initialization
        
        :param pathList list: The list of paths where to search a pyconf.
        '''
        self.pathList = pathList
        if verbose:
          for path in pathList:
            if not os.path.isdir(path):
              logger.warning("ConfigOpener inexisting directory: %s" % path)

    def __call__(self, name):
        if os.path.isabs(name):
            return src.pyconf.ConfigInputStream(open(name, 'rb'))
        else:
            return src.pyconf.ConfigInputStream(open(osJoin(self.get_path(name), name), 'rb'))
        raise IOError(_("Configuration file '%s' not found") % name)

    def get_path( self, name ):
        '''The method that returns the entire path of the pyconf searched
        returns first found in self.pathList directories

        :param name str: The name of the searched pyconf.
        '''
        for path in self.pathList:
            if os.path.exists(osJoin(path, name)):
                return path
        raise IOError(_("Configuration file '%s' not found") % name)

class ConfigManager:
    '''Class that manages the read of all the configuration files of salomeTools
    '''
    def __init__(self, datadir=None):
        pass

    def _create_vars(self, application=None, command=None, datadir=None):
        '''Create a dictionary that stores all information about machine,
           user, date, repositories, etc...
        
        :param application str: The application for which salomeTools is called.
        :param command str: The command that is called.
        :param datadir str: The repository that contain external data 
                            for salomeTools.
        :return: The dictionary that stores all information.
        :rtype: dict
        '''
        var = {}      
        var['user'] = src.architecture.get_user()
        var['salometoolsway'] = os.path.dirname( os.path.dirname(os.path.abspath(__file__)))
        var['srcDir'] =  osJoin(var['salometoolsway'], 'src')
        var['internal_dir'] =  osJoin(var['srcDir'], 'internal_config')
        var['sep']= os.path.sep
        if src.architecture.is_windows():
          var['scriptExtension'] = '.bat'
        else:
          var['scriptExtension'] = '.sh'
        
        # datadir has a default location
        var['datadir'] =  osJoin(var['salometoolsway'], 'data')
        if datadir is not None:
            var['datadir'] = datadir

        var['personalDir'] =  osJoin(os.path.expanduser('~'), '.salomeTools')
        src.ensure_path_exists(var['personalDir'])

        var['personal_applications_dir'] =  osJoin(var['personalDir'], "Applications")
        src.ensure_path_exists(var['personal_applications_dir'])
        
        var['personal_products_dir'] =  osJoin(var['personalDir'], "products")
        src.ensure_path_exists(var['personal_products_dir'])
        
        var['personal_archives_dir'] =  osJoin(var['personalDir'], "Archives")
        src.ensure_path_exists(var['personal_archives_dir'])

        var['personal_jobs_dir'] =  osJoin(var['personalDir'], "Jobs")
        src.ensure_path_exists(var['personal_jobs_dir'])

        var['personal_machines_dir'] =  osJoin(var['personalDir'], "Machines")
        src.ensure_path_exists(var['personal_machines_dir'])

        # read linux distributions dictionary
        distrib_cfg = src.pyconf.Config( osJoin(var['srcDir'], 'internal_config', 'distrib.pyconf'))
        
        # set platform parameters
        dist_name = src.architecture.get_distribution(codes=distrib_cfg.DISTRIBUTIONS)
        dist_version = src.architecture.get_distrib_version(dist_name)
        dist_version_full = src.architecture.get_version_XY()
        dist = dist_name + dist_version
        
        var['dist_name'] = dist_name
        var['dist_version'] = dist_version
        var['dist'] = dist
        var['dist_ref'] = dist_name + dist_version_full
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
                    datadir=None):
        '''get the config from all the configuration files.
        
        :param application str: The application for which salomeTools is called.
        :param options class Options: The general salomeToos
                                      options (--overwrite or -l5, for example)
        :param command str: The command that is called.
        :param datadir str: The repository that contain 
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
        var = self._create_vars(application=application, command=command, datadir=datadir)
        # DBG.write("create_vars", var, DBG.isDeveloper())

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
                             osJoin(cfg.VARS.srcDir, 'internal_config')])
        try:
            if src.architecture.is_windows(): # special internal config for windows
                internal_cfg = src.pyconf.Config(open( osJoin(cfg.VARS.srcDir,
                                        'internal_config', 'salomeTools_win.pyconf')))
            else:
                internal_cfg = src.pyconf.Config(open( osJoin(cfg.VARS.srcDir,
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
        # Load LOCAL config file
        # search only in the data directory
        src.pyconf.streamOpener = ConfigOpener([cfg.VARS.datadir])
        try:
            local_cfg = src.pyconf.Config(open( osJoin(cfg.VARS.datadir,
                                                           'local.pyconf')),
                                         PWD = ('LOCAL', cfg.VARS.datadir) )
        except src.pyconf.ConfigError as e:
            raise src.SatException(_("Error in configuration file: "
                                     "local.pyconf\n  %(error)s") % \
                {'error': str(e) })
        except IOError as error:
            e = str(error)
            raise src.SatException( e );
        merger.merge(cfg, local_cfg)

        # When the key is "default", put the default value
        if cfg.LOCAL.base == "default":
            cfg.LOCAL.base = os.path.abspath(osJoin(cfg.VARS.salometoolsway, "..", "BASE"))
        if cfg.LOCAL.workdir == "default":
            cfg.LOCAL.workdir = os.path.abspath(osJoin(cfg.VARS.salometoolsway, ".."))
        if cfg.LOCAL.log_dir == "default":
            cfg.LOCAL.log_dir = os.path.abspath(osJoin(cfg.VARS.salometoolsway, "..", "LOGS"))

        if cfg.LOCAL.archive_dir == "default":
            cfg.LOCAL.archive_dir = os.path.abspath( osJoin(cfg.VARS.salometoolsway, "..", "ARCHIVES"))

        # if the sat tag was not set permanently by user
        if cfg.LOCAL.tag == "unknown":
            # get the tag with git, and store it
            sat_version=src.system.git_describe(cfg.VARS.salometoolsway) 
            if sat_version == False:
                sat_version=cfg.INTERNAL.sat_version
            cfg.LOCAL.tag=sat_version
                

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["LOCAL"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        # =====================================================================
        # Load the PROJECTS
        projects_cfg = src.pyconf.Config()
        projects_cfg.addMapping("PROJECTS",
                                src.pyconf.Mapping(projects_cfg),
                                "The projects\n")
        projects_cfg.PROJECTS.addMapping("projects",
                                src.pyconf.Mapping(cfg.PROJECTS),
                                "The projects definition\n")
        
        for project_pyconf_path in cfg.PROJECTS.project_file_paths:
            if not os.path.isabs(project_pyconf_path):
                # for a relative path (archive case) we complete with sat path
                project_pyconf_path = os.path.join(cfg.VARS.salometoolsway,
                                                  project_pyconf_path)
            if not os.path.exists(project_pyconf_path):
                msg = _("WARNING: The project file %s cannot be found. "
                        "It will be ignored\n" % project_pyconf_path)
                sys.stdout.write(msg)
                continue
            project_name = os.path.basename(
                                    project_pyconf_path)[:-len(".pyconf")]
            try:
                project_pyconf_dir = os.path.dirname(project_pyconf_path)
                project_cfg = src.pyconf.Config(open(project_pyconf_path),
                                                PWD=("", project_pyconf_dir))
            except Exception as e:
                msg = _("ERROR: Error in configuration file: "
                                 "%(file_path)s\n  %(error)s\n") % \
                            {'file_path' : project_pyconf_path, 'error': str(e) }
                sys.stdout.write(msg)
                continue
            projects_cfg.PROJECTS.projects.addMapping(project_name,
                             src.pyconf.Mapping(projects_cfg.PROJECTS.projects),
                             "The %s project\n" % project_name)
            projects_cfg.PROJECTS.projects[project_name]=project_cfg
            projects_cfg.PROJECTS.projects[project_name]["file_path"] = \
                                                        project_pyconf_path
            # store the project tag if any
            product_project_git_tag = src.system.git_describe(os.path.dirname(project_pyconf_path))
            if product_project_git_tag:
                projects_cfg.PROJECTS.projects[project_name]["git_tag"] = product_project_git_tag
            else:
                projects_cfg.PROJECTS.projects[project_name]["git_tag"] = "unknown"
                   
        merger.merge(cfg, projects_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["PROJECTS"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec
        
        # =====================================================================
        # Create the paths where to search the application configurations, 
        # the product configurations, the products archives, 
        # the jobs configurations and the machines configurations
        cfg.addMapping("PATHS", src.pyconf.Mapping(cfg), "The paths\n")
        cfg.PATHS["APPLICATIONPATH"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS.APPLICATIONPATH.append(cfg.VARS.personal_applications_dir, "")

        
        cfg.PATHS["PRODUCTPATH"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS.PRODUCTPATH.append(cfg.VARS.personal_products_dir, "")
        cfg.PATHS["ARCHIVEPATH"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS.ARCHIVEPATH.append(cfg.VARS.personal_archives_dir, "")
        cfg.PATHS["ARCHIVEFTP"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS["JOBPATH"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS.JOBPATH.append(cfg.VARS.personal_jobs_dir, "")
        cfg.PATHS["MACHINEPATH"] = src.pyconf.Sequence(cfg.PATHS)
        cfg.PATHS.MACHINEPATH.append(cfg.VARS.personal_machines_dir, "")
        cfg.PATHS["LICENCEPATH"] = src.pyconf.Sequence(cfg.PATHS)

        # initialise the path with local directory
        cfg.PATHS["ARCHIVEPATH"].append(cfg.LOCAL.archive_dir, "")

        # Loop over the projects in order to complete the PATHS variables
        # as /data/tmpsalome/salome/prerequis/archives for example ARCHIVEPATH
        for project in cfg.PROJECTS.projects:
            for PATH in ["APPLICATIONPATH",
                         "PRODUCTPATH",
                         "ARCHIVEPATH", #comment this for default archive  	#8646
                         "ARCHIVEFTP",
                         "JOBPATH",
                         "MACHINEPATH",
                         "LICENCEPATH"]:
                if PATH not in cfg.PROJECTS.projects[project]:
                    continue
                pathlist=cfg.PROJECTS.projects[project][PATH].split(":")
                for path in pathlist:
                    cfg.PATHS[PATH].append(path, "")
        
        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["PATHS"]):
            exec('cfg.' + rule) # this cannot be factorized because of the exec

        # AT END append APPLI_TEST directory in APPLICATIONPATH, for unittest
        appli_test_dir =  osJoin(satdir, "test", "APPLI_TEST")
        if appli_test_dir not in cfg.PATHS.APPLICATIONPATH:
          cfg.PATHS.APPLICATIONPATH.append(appli_test_dir, "unittest APPLI_TEST path")

        # =====================================================================
        # Load APPLICATION config file
        if application is not None:
            # search APPLICATION file in all directories in configPath
            cp = cfg.PATHS.APPLICATIONPATH
            src.pyconf.streamOpener = ConfigOpener(cp)
            do_merge = True
            try:
                application_cfg = src.pyconf.Config(application + '.pyconf')
            except IOError as e:
                raise src.SatException(
                   _("%s, use 'config --list' to get the list of available applications.") % e)
            except src.pyconf.ConfigError as e:
                if (not ('-e' in parser.parse_args()[1]) 
                                         or ('--edit' in parser.parse_args()[1]) 
                                         and command == 'config'):
                    raise src.SatException(_("Error in configuration file: "
                                             "%(application)s.pyconf\n "
                                             " %(error)s") % \
                        { 'application': application, 'error': str(e) } )
                else:
                    sys.stdout.write(src.printcolors.printcWarning(
                                        "There is an error in the file"
                                        " %s.pyconf.\n" % cfg.VARS.application))
                    do_merge = False
            except Exception as e:
                if (not ('-e' in parser.parse_args()[1]) 
                                        or ('--edit' in parser.parse_args()[1]) 
                                        and command == 'config'):
                    sys.stdout.write(src.printcolors.printcWarning("%s\n" % str(e)))
                    raise src.SatException(_("Error in configuration file:"
                                             " %(application)s.pyconf\n") % \
                        { 'application': application} )
                else:
                    sys.stdout.write(src.printcolors.printcWarning(
                                "There is an error in the file"
                                " %s.pyconf. Opening the file with the"
                                " default viewer\n" % cfg.VARS.application))
                    sys.stdout.write("The error:"
                                 " %s\n" % src.printcolors.printcWarning(
                                                                      str(e)))
                    do_merge = False
        
            else:
                cfg['open_application'] = 'yes'
        # =====================================================================
        # Load product config files in PRODUCTS section
        products_cfg = src.pyconf.Config()
        products_cfg.addMapping("PRODUCTS",
                                src.pyconf.Mapping(products_cfg),
                                "The products\n")
        if application is not None:
            src.pyconf.streamOpener = ConfigOpener(cfg.PATHS.PRODUCTPATH)
            for product_name in application_cfg.APPLICATION.products.keys():
                # Loop on all files that are in softsDir directory
                # and read their config
                product_file_name = product_name + ".pyconf"
                product_file_path = src.find_file_in_lpath(product_file_name, cfg.PATHS.PRODUCTPATH)
                if product_file_path:
                    products_dir = os.path.dirname(product_file_path)
                    # for a relative path (archive case) we complete with sat path
                    if not os.path.isabs(products_dir):
                        products_dir = os.path.join(cfg.VARS.salometoolsway,
                                                    products_dir)
                    try:
                        prod_cfg = src.pyconf.Config(open(product_file_path),
                                                     PWD=("", products_dir))
                        prod_cfg.from_file = product_file_path
                        products_cfg.PRODUCTS[product_name] = prod_cfg
                    except Exception as e:
                        msg = _(
                            "WARNING: Error in configuration file"
                            ": %(prod)s\n  %(error)s" % \
                            {'prod' :  product_name, 'error': str(e) })
                        sys.stdout.write(msg)
            
            merger.merge(cfg, products_cfg)
            
            # apply overwrite from command line if needed
            for rule in self.get_command_line_overrides(options, ["PRODUCTS"]):
                exec('cfg.' + rule) # this cannot be factorized because of the exec
            
            if do_merge:
                merger.merge(cfg, application_cfg)

                # default launcher name ('salome')
                if ('profile' in cfg.APPLICATION and 
                    'launcher_name' not in cfg.APPLICATION.profile):
                    cfg.APPLICATION.profile.launcher_name = 'salome'

                # apply overwrite from command line if needed
                for rule in self.get_command_line_overrides(options,
                                                             ["APPLICATION"]):
                    # this cannot be factorized because of the exec
                    exec('cfg.' + rule)
            
        # =====================================================================
        # load USER config
        self.set_user_config_file(cfg)
        user_cfg_file = self.get_user_config_file()
        user_cfg = src.pyconf.Config(open(user_cfg_file))
        merger.merge(cfg, user_cfg)

        # apply overwrite from command line if needed
        for rule in self.get_command_line_overrides(options, ["USER"]):
            exec('cfg.' + rule) # this cannot be factorize because of the exec
        
        # remove application products "blacklisted" in rm_products field
        if "APPLICATION" in cfg and "rm_products" in cfg.APPLICATION:
            for prod_to_remove in cfg.APPLICATION.rm_products:
                cfg.APPLICATION.products.__delitem__(prod_to_remove)
            # remove rm_products section after usage
            cfg.APPLICATION.__delitem__("rm_products")
        return cfg

    def set_user_config_file(self, config):
        '''Set the user config file name and path.
        If necessary, build it from another one or create it from scratch.
        
        :param config class 'src.pyconf.Config': The global config 
                                                 (containing all pyconf).
        '''
        # get the expected name and path of the file
        self.config_file_name = 'SAT.pyconf'
        self.user_config_file_path =  osJoin(config.VARS.personalDir, self.config_file_name)
        
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

        user_cfg.USER.addMapping('cvs_user', config.VARS.user,
            "This is the user name used to access salome cvs base.\n")
        user_cfg.USER.addMapping('svn_user', config.VARS.user,
            "This is the user name used to access salome svn base.\n")
        user_cfg.USER.addMapping('output_verbose_level', 3,
            "This is the default output_verbose_level you want."
            " 0=>no output, 5=>debug.\n")
        user_cfg.USER.addMapping('publish_dir', 
                                  osJoin(os.path.expanduser('~'),
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

        src.ensure_path_exists(config.VARS.personalDir)
        src.ensure_path_exists( osJoin(config.VARS.personalDir,
                                            'Applications'))

        f = open(cfg_name, 'w')
        user_cfg.__save__(f)
        f.close()

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

def check_path(path, ext=[]):
    '''Construct a text with the input path and "not found" if it does not
       exist.
    
    :param path Str: the path to check.
    :param ext List: An extension. Verify that the path extension 
                     is in the list
    :return: The string of the path with information
    :rtype: Str
    '''
    # check if file exists
    if not os.path.exists(path):
        return "'%s'" % path + " " + src.printcolors.printcError(_(
                                                            "** not found"))

    # check extension
    if len(ext) > 0:
        fe = os.path.splitext(path)[1].lower()
        if fe not in ext:
            return "'%s'" % path + " " + src.printcolors.printcError(_(
                                                        "** bad extension"))

    return path

def show_product_info(config, name, logger):
    '''Display on the terminal and logger information about a product.
    
    :param config Config: the global configuration.
    :param name Str: The name of the product
    :param logger Logger: The logger instance to use for the display
    '''
    
    logger.write(_("%s is a product\n") % src.printcolors.printcLabel(name), 2)
    pinfo = src.product.get_product_config(config, name)
    
    if "depend" in pinfo:
        src.printcolors.print_value(logger, "depends on", sorted(pinfo.depend), 2)

    if "opt_depend" in pinfo:
        src.printcolors.print_value(logger, "optional", sorted(pinfo.opt_depend), 2)

    if "build_depend" in pinfo:
        src.printcolors.print_value(logger, "build depend on", sorted(pinfo.build_depend), 2)


    # information on pyconf
    logger.write("\n", 2)
    logger.write(src.printcolors.printcLabel("configuration:") + "\n", 2)
    if "from_file" in pinfo:
        src.printcolors.print_value(logger,
                                    "pyconf file path",
                                    pinfo.from_file,
                                    2)
    if "section" in pinfo:
        src.printcolors.print_value(logger,
                                    "section",
                                    pinfo.section,
                                    2)

    # information on prepare
    logger.write("\n", 2)
    logger.write(src.printcolors.printcLabel("prepare:") + "\n", 2)

    is_dev = src.product.product_is_dev(pinfo)
    method = pinfo.get_source
    if is_dev:
        method += " (dev)"
    src.printcolors.print_value(logger, "get method", method, 2)

    if method == 'cvs':
        src.printcolors.print_value(logger, "server", pinfo.cvs_info.server, 2)
        src.printcolors.print_value(logger, "base module",
                                    pinfo.cvs_info.module_base, 2)
        src.printcolors.print_value(logger, "source", pinfo.cvs_info.source, 2)
        src.printcolors.print_value(logger, "tag", pinfo.cvs_info.tag, 2)

    elif method == 'svn':
        src.printcolors.print_value(logger, "repo", pinfo.svn_info.repo, 2)

    elif method == 'git':
        src.printcolors.print_value(logger, "repo", pinfo.git_info.repo, 2)
        src.printcolors.print_value(logger, "tag", pinfo.git_info.tag, 2)

    elif method == 'archive':
        src.printcolors.print_value(logger,
                                    "get from",
                                    check_path(pinfo.archive_info.archive_name),
                                    2)

    if 'patches' in pinfo:
        for patch in pinfo.patches:
            src.printcolors.print_value(logger, "patch", check_path(patch), 2)

    if src.product.product_is_fixed(pinfo):
        src.printcolors.print_value(logger, "install_dir",
                                    check_path(pinfo.install_dir), 2)

    if src.product.product_is_native(pinfo) or src.product.product_is_fixed(pinfo):
        return
    
    # information on compilation
    if src.product.product_compiles(pinfo):
        logger.write("\n", 2)
        logger.write(src.printcolors.printcLabel("compile:") + "\n", 2)
        src.printcolors.print_value(logger,
                                    "compilation method",
                                    pinfo.build_source,
                                    2)
        
        if pinfo.build_source == "script" and "compil_script" in pinfo:
            src.printcolors.print_value(logger, 
                                        "Compilation script", 
                                        pinfo.compil_script, 
                                        2)
        
        if 'nb_proc' in pinfo:
            src.printcolors.print_value(logger, "make -j", pinfo.nb_proc, 2)
    
        src.printcolors.print_value(logger, 
                                    "source dir", 
                                    check_path(pinfo.source_dir), 
                                    2)
        if 'install_dir' in pinfo:
            src.printcolors.print_value(logger, 
                                        "build dir", 
                                        check_path(pinfo.build_dir), 
                                        2)
            src.printcolors.print_value(logger, 
                                        "install dir", 
                                        check_path(pinfo.install_dir), 
                                        2)
        else:
            logger.write("  " + 
                         src.printcolors.printcWarning(_("no install dir")) + 
                         "\n", 2)

        src.printcolors.print_value(logger, "debug ", pinfo.debug, 2)
        src.printcolors.print_value(logger, "verbose ", pinfo.verbose, 2)
        src.printcolors.print_value(logger, "hpc ", pinfo.hpc, 2)
        src.printcolors.print_value(logger, "dev ", pinfo.dev, 2)

    else:
        logger.write("\n", 2)
        msg = _("This product does not compile")
        logger.write("%s\n" % msg, 2)

    # information on environment
    logger.write("\n", 2)
    logger.write(src.printcolors.printcLabel("environ :") + "\n", 2)
    if "environ" in pinfo and "env_script" in pinfo.environ:
        src.printcolors.print_value(logger, 
                                    "script", 
                                    check_path(pinfo.environ.env_script), 
                                    2)

    # display run-time environment
    zz = src.environment.SalomeEnviron(config,
                                       src.fileEnviron.ScreenEnviron(logger), 
                                       False)
    zz.set_python_libdirs()
    zz.set_a_product(name, logger)
    logger.write("\n", 2)


def show_patchs(config, logger):
  '''Prints all the used patchs in the application.

  :param config Config: the global configuration.
  :param logger Logger: The logger instance to use for the display
  '''
  oneOrMore = False
  for product in sorted(config.APPLICATION.products):
    try:
      product_info = src.product.get_product_config(config, product)
      if src.product.product_has_patches(product_info):
        oneOrMore = True
        logger.write("%s:\n" % product, 1)
        for i in product_info.patches:
          logger.write(src.printcolors.printcInfo("    %s\n" % i), 1)
    except Exception as e:
      msg = "problem on product %s\n%s\n" % (product, str(e))
      logger.error(msg)

  if oneOrMore:
    logger.write("\n", 1)
  else:
    logger.write("No patchs found\n", 1)

def check_install_system(config, logger):
  '''Check the installation of all (declared) system products

  :param config Config: the global configuration.
  :param logger Logger: The logger instance to use for the display
  '''
  # get the command to use for checking the system dependencies
  # (either rmp or apt)
  check_cmd=src.system.get_pkg_check_cmd(config.VARS.dist_name)
  logger.write("\nCheck the system dependencies declared in the application\n",1)
  pkgmgr=check_cmd[0]
  run_dep_ko=[] # list of missing run time dependencies
  build_dep_ko=[] # list of missing compile time dependencies
  for product in sorted(config.APPLICATION.products):
    try:
      product_info = src.product.get_product_config(config, product)
      if src.product.product_is_native(product_info):
        # if the product is native, get (in two dictionnaries the runtime and compile time 
        # system dependencies with the status (OK/KO)
        run_pkg,build_pkg=src.product.check_system_dep(config.VARS.dist, check_cmd, product_info)
        #logger.write("\n*** %s ***\n" % product, 1)
        for pkg in run_pkg:
            logger.write("\n   - "+pkg + " : " + run_pkg[pkg], 1)
            if "KO" in run_pkg[pkg]:
                run_dep_ko.append(pkg)
        for pkg in build_pkg:
            logger.write("\n   - "+pkg + " : " + build_pkg[pkg], 1)
            if "KO" in build_pkg[pkg]:
                build_dep_ko.append(pkg)
        #  logger.write(src.printcolors.printcInfo("    %s\n" % i), 1)

    except Exception as e:
      msg = "\nproblem with the check of system prerequisite %s\n%s\n" % (product, str(e))
      logger.error(msg)
      raise Exception(msg)

  logger.write("\n\n",1)
  if run_dep_ko:
      msg="Some run time system dependencies are missing!\n"+\
          "Please install them with %s before running salome" % pkgmgr
      logger.warning(msg)
      logger.write("missing run time dependencies : ",1)
      for md in run_dep_ko: 
        logger.write(md+" ",1)
      logger.write("\n\n")
        
  if build_dep_ko:
      msg="Some compile time system dependencies are missing!\n"+\
          "Please install them with %s before compiling salome" % pkgmgr
      logger.warning(msg)
      logger.write("missing compile time dependencies : ",1)
      for md in build_dep_ko: 
        logger.write(md+" ",1)
      logger.write("\n\n")
    

def show_dependencies(config, products, logger):
    '''Prints dependencies of products in the application.

    :param config Config: the global configuration.
    :param logger Logger: The logger instance to use for the display
    '''

    from compile import get_dependencies_graph,depth_search_graph,find_path_graph
    # Get the list of all application products, and create its dependency graph
    all_products_infos = src.product.get_products_infos(config.APPLICATION.products,config)
    all_products_graph=get_dependencies_graph(all_products_infos, compile_time=False)

    products_list=[]
    product_liste_name=""
    if products is None:
        products_list=config.APPLICATION.products
        products_graph = all_products_graph
    else:
        # 1. Extend the list with all products that depends upon the given list of products
        products_list=products
        product_liste_name="_".join(products)
        visited=[]
        for p_name in products_list:
            visited=depth_search_graph(all_products_graph, p_name, visited)
        products_infos = src.product.get_products_infos(visited, config)
        products_graph = get_dependencies_graph(products_infos, compile_time=False)

        # 2. Extend the list with all the dependencies of the given list of products
        children=[]
        for n in all_products_graph:
            # for all products (that are not in products_list):
            # if we we find a path from the product to the product list,
            # then we product is a child and we add it to the children list 
            if (n not in children) and (n not in products_list):
                if find_path_graph(all_products_graph, n, products_list):
                    children = children + [n]
        products_infos_rev = src.product.get_products_infos(children, config)
        products_graph_rev = get_dependencies_graph(products_infos_rev, compile_time=False)

    logger.write("Dependency graph (python format)\n%s\n" % products_graph, 3)

    gv_file_name='%s_%s_dep.gv' % (config.VARS.application,product_liste_name)
    logger.write("\nDependency graph (graphviz format) written in file %s\n" % 
                 src.printcolors.printcLabel(gv_file_name), 3)
    with open(gv_file_name,"w") as f:
        f.write("digraph G {\n")
        for p in products_graph:
            for dep in products_graph[p]:
                f.write ("\t%s -> %s\n" % (p,dep))
        f.write("}\n")
        

    if products is not None:
        # if a list of products was given, produce also the reverse dependencies
        gv_revfile_name='%s_%s_rev_dep.gv' % (config.VARS.application,product_liste_name)
        logger.write("\nReverse dependency graph (graphviz format) written in file %s\n" % 
                 src.printcolors.printcLabel(gv_revfile_name), 3)
        with open(gv_revfile_name,"w") as rf:
            rf.write("digraph G {\n")
            for p in products_graph_rev:
                for dep in products_graph_rev[p]:
                    rf.write ("\t%s -> %s\n" % (p,dep))
            rf.write("}\n")
    
    graph_cmd = "dot -Tpdf %s -o %s.pdf" % (gv_file_name,gv_file_name)
    logger.write("\nTo generate a graph use dot tool : \n  %s" % 
                 src.printcolors.printcLabel(graph_cmd), 3)
 
def show_install_dir(config, logger):
  '''Prints all the used installed directories in the application.

  :param config Config: the global configuration.
  :param logger Logger: The logger instance to use for the display
  '''
  for product in sorted(config.APPLICATION.products):
    try:
      product_info = src.product.get_product_config(config, product)
      install_path=src.Path(product_info.install_dir)
      if (src.product.product_is_native(product_info)):
          install_path="Native"
      elif (src.product.product_is_fixed(product_info)):
          install_path+=" (Fixed)"
      logger.write("%s : %s\n" % (product, install_path) , 1)
    except Exception as e:
      msg = "problem on product %s\n%s\n" % (product, str(e))
      logger.error(msg)
  logger.write("\n", 1)


def show_properties(config, logger):
  '''Prints all the used properties in the application.

  :param config Config: the global configuration.
  :param logger Logger: The logger instance to use for the display
  '''
  if "properties" in config.APPLICATION:
      # some properties are defined at application level, we display them
      logger.write("Application properties:\n", 1)
      for prop in config.APPLICATION.properties:
          logger.write(src.printcolors.printcInfo("    %s : %s\n" % (prop, config.APPLICATION.properties[prop])), 1)
  oneOrMore = False
  for product in sorted(config.APPLICATION.products):
    try:
      product_info = src.product.get_product_config(config, product)
      done = False
      try:
        for prop in product_info.properties:
          if not done:
            logger.write("%s:\n" % product, 1)
            done = True
          oneOrMore = True
          logger.write(src.printcolors.printcInfo("    %s : %s\n" % (prop, product_info.properties[prop])), 1)
      except Exception as e:
        pass
    except Exception as e:
      # logger.write(src.printcolors.printcInfo("    %s\n" % "no properties"), 1)
      msg = "problem on product %s\n%s\n" % (product, e)
      logger.error(msg)

  if oneOrMore:
    logger.write("\n", 1)
  else:
    logger.write("No properties found\n", 1)

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
    
    # Make sure that the path does not ends with a point
    if path.endswith('.'):
        path = path[:-1]
    
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

def get_config_children(config, args):
    '''Gets the names of the children of the given parameter.
       Useful only for completion mechanism
    
    :param config Config: The configuration where to read the values
    :param args: The path in the config from which get the keys
    '''
    vals = []
    rootkeys = config.keys()
    
    if len(args) == 0:
        # no parameter returns list of root keys
        vals = rootkeys
    else:
        parent = args[0]
        pos = parent.rfind('.')
        if pos < 0:
            # Case where there is only on key as parameter.
            # For example VARS
            vals = [m for m in rootkeys if m.startswith(parent)]
        else:
            # Case where there is a part from a key
            # for example VARS.us  (for VARS.user)
            head = parent[0:pos]
            tail = parent[pos+1:]
            try:
                a = config.getByPath(head)
                if dir(a).__contains__('keys'):
                    vals = map(lambda x: head + '.' + x,
                               [m for m in a.keys() if m.startswith(tail)])
            except:
                pass

    for v in sorted(vals):
        sys.stdout.write("%s\n" % v)

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the config command description.
    :rtype: str
    '''
    return _("The config command allows manipulation "
             "and operation on config files.\n\nexample:\nsat config "
             "SALOME-master --info ParaView")
    

def run(args, runner, logger):
    '''method that is called when salomeTools is called with config parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)

    # Only useful for completion mechanism : print the keys of the config
    if options.schema:
        get_config_children(runner.cfg, args)
        return

    # case : print a value of the config
    if options.value:
        if options.value == ".":
            # if argument is ".", print all the config
            for val in sorted(runner.cfg.keys()):
                print_value(runner.cfg, val, not options.no_label, logger)
        else:
            print_value(runner.cfg, options.value, not options.no_label, logger, 
                        level=0, show_full_path=False)
    
    # case : print a debug value of the config
    if options.debug:
        if options.debug == ".":
            # if argument is ".", print all the config
            res = DBG.indent(DBG.getStrConfigDbg(runner.cfg))
            logger.write("\nConfig of application %s:\n\n%s\n" % (runner.cfg.VARS.application, res))
        else:
            if options.debug[0] == ".": # accept ".PRODUCT.etc" as "PRODUCT.etc"
              od = options.debug[1:]
            else:
              od = options.debug
            try:
              aCode = "a = runner.cfg.%s" % od
              # https://stackoverflow.com/questions/15086040/behavior-of-exec-function-in-python-2-and-python-3
              aDict = {"runner": runner}
              exec(aCode, globals(), aDict)
              # DBG.write("globals()", globals(), True)
              # DBG.write("aDict", aDict, True)
              res = DBG.indent(DBG.getStrConfigDbg(aDict["a"]))
              logger.write("\nConfig.%s of application %s:\n\n%s\n" % (od, runner.cfg.VARS.application, res))
            except Exception as e:
              msg = "\nConfig.%s of application %s: Unknown pyconf key\n" % (od, runner.cfg.VARS.application)
              logger.write(src.printcolors.printcError(msg), 1)

    
    # case : edit user pyconf file or application file
    if options.edit:
        editor = runner.cfg.USER.editor
        if ('APPLICATION' not in runner.cfg and
                       'open_application' not in runner.cfg): # edit user pyconf
            usercfg =  osJoin(runner.cfg.VARS.personalDir,
                                   'SAT.pyconf')
            logger.write(_("Opening %s\n" % usercfg), 3)
            src.system.show_in_editor(editor, usercfg, logger)
        else:
            # search for file <application>.pyconf and open it
            for path in runner.cfg.PATHS.APPLICATIONPATH:
                pyconf_path =  osJoin(path,
                                    runner.cfg.VARS.application + ".pyconf")
                if os.path.exists(pyconf_path):
                    logger.write(_("Opening %s\n" % pyconf_path), 3)
                    src.system.show_in_editor(editor, pyconf_path, logger)
                    break
    
    # case : give information about the product(s) in parameter
    if options.products:
      if options.info is not None:
        logger.warning('options.products %s overrides options.info %s' % (options.products, options.info))
      options.info = options.products

    if options.info:
      # DBG.write("products", sorted(runner.cfg.APPLICATION.products.keys()), True)
      src.check_config_has_application(runner.cfg)
      taggedProducts = src.getProductNames(runner.cfg, options.info, logger)
      DBG.write("tagged products", sorted(taggedProducts))
      for prod in sorted(taggedProducts):
        if prod in runner.cfg.APPLICATION.products:
          try:
            if len(taggedProducts) > 1:
              logger.write("#################### ", 2)
            show_product_info(runner.cfg, prod, logger)
          except Exception as e:
            msg = "problem on product %s\n%s\n" % (prod, str(e))
            logger.error(msg)
          # return
        else:
          msg = _("%s is not a product of %s.\n") % \
                (prod, runner.cfg.VARS.application)
          logger.warning(msg)
          #raise Exception(msg)
    
    # case : copy an existing <application>.pyconf 
    # to ~/.salomeTools/Applications/LOCAL_<application>.pyconf
    if options.copy:
        # product is required
        src.check_config_has_application( runner.cfg )

        # get application file path 
        source = runner.cfg.VARS.application + '.pyconf'
        source_full_path = ""
        for path in runner.cfg.PATHS.APPLICATIONPATH:
            # ignore personal directory
            if path == runner.cfg.VARS.personalDir:
                continue
            # loop on all directories that can have pyconf applications
            zz =  osJoin(path, source)
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
            elif 'copy_prefix' in runner.cfg.INTERNAL.config:
                # use prefix
                dest = (runner.cfg.INTERNAL.config.copy_prefix 
                        + runner.cfg.VARS.application)
            else:
                # use same name as source
                dest = runner.cfg.VARS.application
                
            # the full path
            dest_file =  osJoin(runner.cfg.VARS.personalDir,
                                     'Applications', dest + '.pyconf')
            if os.path.exists(dest_file):
                raise src.SatException(_("A personal application"
                                         " '%s' already exists") % dest)
            
            # perform the copy
            shutil.copyfile(source_full_path, dest_file)
            logger.write(_("%s has been created.\n") % dest_file)
    
    # case : display all the available pyconf applications
    if options.list:
        lproduct = list()
        # search in all directories that can have pyconf applications
        for path in runner.cfg.PATHS.APPLICATIONPATH:
            # print a header
            if not options.no_label:
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
                        if path.startswith(runner.cfg.VARS.personalDir) \
                                    and not options.no_label:
                            logger.write("%s*\n" % appliname)
                        else:
                            logger.write("%s\n" % appliname)
                            
            logger.write("\n")

    # case: print all the products name of the application (internal use for completion)
    if options.completion:
        for product_name in runner.cfg.APPLICATION.products.keys():
            logger.write("%s\n" % product_name)
        
    # case : give a synthetic view of all patches used in the application
    if options.show_patchs:
        src.check_config_has_application(runner.cfg)
        # Print some informations
        logger.write(_('Patchs of application %s\n') %
                    src.printcolors.printcLabel(runner.cfg.VARS.application), 3)
        logger.write("\n", 2, False)
        show_patchs(runner.cfg, logger)

    # case : give a synthetic view of all install directories used in the application
    if options.show_install:
        src.check_config_has_application(runner.cfg)
        # Print some informations
        logger.write(_('Installation directories of application %s\n') %
                    src.printcolors.printcLabel(runner.cfg.VARS.application), 3)
        logger.write("\n", 2, False)
        show_install_dir(runner.cfg, logger)

    # case : give a synthetic view of all dependencies between products of the application
    if options.show_dependencies:
        src.check_config_has_application(runner.cfg)
        # Print some informations
        logger.write(_('List of run-time dependencies of the application %s, product by product\n') %
                    src.printcolors.printcLabel(runner.cfg.VARS.application), 3)
        logger.write("\n", 2, False)
        show_dependencies(runner.cfg, options.products, logger)

    # case : give a synthetic view of all patches used in the application
    if options.show_properties:
        src.check_config_has_application(runner.cfg)

        # Print some informations
        logger.write(_('Properties of application %s\n') %
                    src.printcolors.printcLabel(runner.cfg.VARS.application), 3)
        logger.write("\n", 2, False)
        show_properties(runner.cfg, logger)

    # check system prerequisites
    if options.check_system:
       check_install_system(runner.cfg, logger)
       pass 
