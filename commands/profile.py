#!/usr/bin/env python
#-*- coding:utf-8 -*-
#  Copyright (C) 2010-2013  CEA/DEN
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
import subprocess

import src

parser = src.options.Options()

parser.add_option( 'p', 'prefix', 'string', 'prefix', _("Where the profile's "
                                                        "sources will be "
                                                        "generated.") )
parser.add_option( 'n', 'name', 'string', 'name', _("Name of the profile's "
                                                    "sources. [Default: "
                                                    "${config.PRODUCT.name}"
                                                    "_PROFILE]") )
parser.add_option( 'f', 'force', 'boolean', 'force', _("Overwrites "
                                                       "existing sources.") )
parser.add_option( 'u', 'no_update', 'boolean', 'no_update', _("Does not update"
                                                               " pyconf file."))
parser.add_option( 'v', 'version', 'string', 'version', _("Version of the "
                                                          "application. [Defa"
                                                          "ult: 1.0]"), '1.0' )
parser.add_option( 's', 'slogan', 'string', 'slogan', _("Slogan of the "
                                                        "application.") )

##################################################

##
# Class that overrides common.Reference
# in order to manipulate fields starting with '@'
class profileReference( src.pyconf.Reference ) :
    def __str__(self):
        s = self.elements[0]
        for tt, tv in self.elements[1:]:
            if tt == src.pyconf.DOT:
                s += '.%s' % tv
            else:
                s += '[%r]' % tv
        if self.type == src.pyconf.BACKTICK:
            return src.pyconf.BACKTICK + s + src.pyconf.BACKTICK
        elif self.type == src.pyconf.AT:
            return src.pyconf.AT + s
        else:
            return src.pyconf.DOLLAR + s

##
# Class that overrides how fields starting with '@' are read.
class profileConfigReader( src.pyconf.ConfigReader ) :
    def parseMapping(self, parent, suffix):
        if self.token[0] == src.pyconf.LCURLY:
            self.match(src.pyconf.LCURLY)
            rv = src.pyconf.Mapping(parent)
            rv.setPath(
               src.pyconf.makePath(object.__getattribute__(parent, 'path'),
                                   suffix))
            self.parseMappingBody(rv)
            self.match(src.pyconf.RCURLY)
        else:
            self.match(src.pyconf.AT)
            __, fn = self.match('"')
            rv = profileReference(self, src.pyconf.AT, fn)
        return rv

##################################################

##
# Describes the command
def description():
    return _("The profile command creates default profile.\nusage: sat profile "
             "[PRODUCT] [-p|--prefix (string)] [-n|--name (string)] [-f|--force"
             "] [-v|--version (string)] [-s|--slogan (string)]")

##
# Gets the profile name
def get_profile_name ( options, config ):
    if options.name :
        res = options.name
    else :
        res = config.APPLICATION.name + "_PROFILE"
    return res

##
# Generates the sources of the profile
def generate_profile_sources( config, options, logger ):
    #Check script app-quickstart.py exists
    kernel_cfg = src.product.get_product_config(config, "KERNEL")
    kernel_root_dir = kernel_cfg.install_dir
    if not src.product.check_installation(kernel_cfg):
        raise src.SatException(_("KERNEL is not installed"))
    script = os.path.join(kernel_root_dir,"bin","salome","app-quickstart.py")
    if not os.path.exists( script ):
        raise src.SatException(_("KERNEL's install has not the script "
                                 "app-quickstart.py"))

    # Check that GUI is installed
    gui_cfg = src.product.get_product_config(config, "GUI")
    gui_root_dir = gui_cfg.install_dir
    if not src.product.check_installation(gui_cfg):
        raise src.SatException(_("GUI is not installed"))

    #Set prefix option passed to app-quickstart.py
    name = get_profile_name ( options, config )
    prefix = os.path.join( options.prefix, name )
    if os.path.exists( prefix ) :
        if not options.force :
            raise src.SatException( _("The path %s already exists, use option"
                                      " --force to remove it." %prefix ) )
        else :
            shutil.rmtree( prefix )

    #Set name option passed to app-quickstart.py
    if name.upper().endswith("_PROFILE"):
        name = name[:-8]

    #Write command line that calls app-quickstart.py
    command = "python %s --prefix=%s --name=%s --modules=_NO_ --version=%s" % (
                                        script, prefix, name, options.version )
    if options.force :
        command += " --force"
    if options.slogan :
        command += " --slogan=%s" % options.slogan
    logger.write("\n>" + command + "\n", 5, False)

    #Run command
    os.environ["KERNEL_ROOT_DIR"] = kernel_root_dir
    os.environ["GUI_ROOT_DIR"] = gui_root_dir
    res = subprocess.call(command,
                    shell=True,
                    env=os.environ,
                    stdout=logger.logTxtFile,
                    stderr=subprocess.STDOUT)
    #Check result of command
    if res != 0:
        raise src.SatException(_("Cannot create application, code = %d\n")%res)
    else:
        logger.write(_("Profile sources were generated in directory %s.\n"%prefix),
                     3)
    return res

##
# Updates the pyconf
def update_pyconf( config, options, logger ):

    #Save previous version
    pyconf = config.VARS.product + '.pyconf'
    pyconfBackup = config.VARS.product + '-backup.pyconf'
    logger.write(_("Updating %(new)s (previous version saved "
                   "as %(old)s).") % { "new": pyconf, "old": pyconfBackup }, 3)
    path = config.getPath( pyconf )
    shutil.copyfile( os.path.join( path, pyconf ),
                     os.path.join( path, pyconfBackup ) )

    #Load config
    cfg = src.pyconf.Config( )
    object.__setattr__( cfg, 'reader', profileConfigReader( cfg ) )
    cfg.load( src.pyconf.defaultStreamOpener( os.path.join( path, pyconf ) ) )

    #Check if profile is in APPLICATION.products
    profile = get_profile_name ( options, config )
    if not profile in cfg.APPLICATION.products:
        cfg.APPLICATION.products.append( profile, None )

    #Check if profile is in APPLICATION
    if not 'profile' in cfg.APPLICATION:
        cfg.APPLICATION.addMapping( 'profile', src.pyconf.Mapping(), None )
        cfg.APPLICATION.profile.addMapping( 'module', profile, None )
        cfg.APPLICATION.profile.addMapping( 'launcher_name',
                                            config.VARS.product.lower(), None )

    #Check if profile info is in PRODUCTS
    if not 'PRODUCTS' in cfg:
        cfg.addMapping( 'PRODUCTS', src.pyconf.Mapping(), None )
        
    if not profile in cfg.PRODUCTS:
        cfg.PRODUCTS.addMapping( profile, src.pyconf.Mapping(), None )
        cfg.PRODUCTS[profile].addMapping( 'default', src.pyconf.Mapping(),
                                          None )
        prf = cfg.TOOLS.common.module_info[profile].default
        prf.addMapping( 'name', profile, None )
        prf.addMapping( 'get_source', 'archive', None )
        prf.addMapping( 'build_source', 'cmake', None )
        prf.addMapping( 'archive_info', src.pyconf.Mapping(), None )
        prf.archive_info.addMapping( 'name',
                                     os.path.join(os.path.abspath(options.prefix),
                                                  profile ), None )
        prf.addMapping( 'source_dir', src.pyconf.Reference(cfg,
                                                           src.pyconf.DOLLAR,
                                                           'APPLICATION.workdir'
                                                           ' + $VARS.sep + "SOU'
                                                           'RCES" + $VARS.sep +'
                                                           ' $name' ), None )
        prf.addMapping( 'build_dir', src.pyconf.Reference(cfg,
                                                          src.pyconf.DOLLAR,
                                                          'APPLICATION.workdir '
                                                          '+ $VARS.sep + "BUILD'
                                                          '" + $VARS.sep + $nam'
                                                          'e' ), None )
        prf.addMapping( 'depend', src.pyconf.Sequence(), None )
        prf.depend.append( 'KERNEL', None )
        prf.depend.append( 'GUI', None )
        prf.depend.append( 'Python', None )
        prf.depend.append( 'Sphinx', None )
        prf.depend.append( 'qt', None )
        prf.addMapping( 'opt_depend', src.pyconf.Sequence(), None )

    #Save config
    f = file( os.path.join( path, pyconf ) , 'w')
    cfg.__save__(f)


##
# Runs the command.
def run(args, runner, logger):
    '''method that is called when salomeTools is called with profile parameter.
    '''
    (options, args) = parser.parse_args(args)
    
    src.check_config_has_application(runner.cfg)

    if options.prefix is None:
        msg = _("The --%s argument is required\n") % "prefix"
        logger.write(src.printcolors.printcWarning(msg), 1)
        return 1
    
    retcode = generate_profile_sources( runner.cfg, options, logger )

    if not options.no_update :
        update_pyconf( runner.cfg, options )

    return retcode
