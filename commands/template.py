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
import string
import shutil
import subprocess
import fnmatch
import re

import src

# Compatibility python 2/3 for input function
# input stays input for python 3 and input = raw_input for python 2
try: 
    input = raw_input
except NameError: 
    pass

# Python 2/3 compatibility for execfile function
try:
    execfile
except:
    def execfile(somefile, global_vars, local_vars):
        with open(somefile) as f:
            code = compile(f.read(), somefile, 'exec')
            exec(code, global_vars, local_vars)

parser = src.options.Options()
parser.add_option('n', 'name', 'string', 'name',
    _("""REQUIRED: the name of the module to create.
\tThe name must be a single word in upper case with only alphanumeric characters.
\tWhen generating a c++ component the module's """
"""name must be suffixed with 'CPP'."""))
parser.add_option('t', 'template', 'string', 'template',
    _('REQUIRED: the template to use.'))
parser.add_option('', 'target', 'string', 'target',
    _('REQUIRED: where to create the module.'))
parser.add_option('', 'param', 'string', 'param',
    _('''Optional: dictionary to generate the configuration for salomeTools.
\tFormat is: --param param1=value1,param2=value2... without spaces
\tNote that when using this option you must supply all the '''
'''values otherwise an error will be raised.'''))
parser.add_option('', 'info', 'boolean', 'info',
    _('Optional: Get information on the template.'), False)

class TParam:
    def __init__(self, param_def, compo_name, dico=None):
        self.default = ""
        self.prompt = ""
        self.check_method = None
        
        if isinstance(param_def, str):
            self.name = param_def
        elif isinstance(param_def, tuple):
            self.name = param_def[0]
            if len(param_def) > 1:
                if dico is not None: self.default = param_def[1] % dico
                else: self.default = param_def[1]
            if len(param_def) > 2: self.prompt = param_def[2]
            if len(param_def) > 3: self.check_method = param_def[3]
        else:
            raise src.SatException(_("ERROR in template parameter definition"))

        self.raw_prompt = self.prompt
        if len(self.prompt) == 0:
            self.prompt = _("value for '%s'") % self.name
        self.prompt += "? "
        if len(self.default) > 0:
            self.prompt += "[%s] " % self.default

    def check_value(self, val):
        if self.check_method is None:
            return len(val) > 0
        return len(val) > 0 and self.check_method(val)

def get_dico_param(dico, key, default):
    if key in dico:
        return dico[key]
    return default

class TemplateSettings:
    def __init__(self, compo_name, settings_file, target):
        self.compo_name = compo_name
        self.dico = None
        self.target = target

        # read the settings
        gdic, ldic = {}, {}
        execfile(settings_file, gdic, ldic)

        # check required parameters in template.info
        missing = []
        for pp in ["file_subst", "parameters"]:
            if not (pp in ldic): missing.append("'%s'" % pp)
        if len(missing) > 0:
            raise src.SatException(_(
                "Bad format in settings file! %s not defined.") % ", ".join(
                                                                       missing))
        
        self.file_subst = ldic["file_subst"]
        self.parameters = ldic['parameters']
        self.info = get_dico_param(ldic, "info", "").strip()
        self.pyconf = get_dico_param(ldic, "pyconf", "")
        self.post_command = get_dico_param(ldic, "post_command", "")

        # get the delimiter for the template
        self.delimiter_char = get_dico_param(ldic, "delimiter", ":sat:")

        # get the ignore filter
        self.ignore_filters = [l.strip() for l in ldic["ignore_filters"].split(',')]

    def has_pyconf(self):
        return len(self.pyconf) > 0

    def get_pyconf_parameters(self):
        if len(self.pyconf) == 0:
            return []
        return re.findall("%\((?P<name>\S[^\)]*)", self.pyconf)

    ##
    # Check if the file needs to be parsed.
    def check_file_for_substitution(self, file_):
        for filter_ in self.ignore_filters:
            if fnmatch.fnmatchcase(file_, filter_):
                return False
        return True

    def check_user_values(self, values):
        if values is None:
            return
        
        # create a list of all parameters (pyconf + list))
        pnames = self.get_pyconf_parameters()
        for p in self.parameters:
            tp = TParam(p, self.compo_name)
            pnames.append(tp.name)
        
        # reduce the list
        pnames = list(set(pnames)) # remove duplicates

        known_values = ["name", "Name", "NAME", "target", self.file_subst]
        known_values.extend(values.keys())
        missing = []
        for p in pnames:
            if p not in known_values:
                missing.append(p)
        
        if len(missing) > 0:
            raise src.SatException(_(
                                 "Missing parameters: %s") % ", ".join(missing))

    def get_parameters(self, conf_values=None):
        if self.dico is not None:
            return self.dico

        self.check_user_values(conf_values)

        # create dictionary with default values
        dico = {}
        dico["name"] = self.compo_name.lower()
        dico["Name"] = self.compo_name.capitalize()
        dico["NAME"] = self.compo_name
        dico["target"] = self.target
        dico[self.file_subst] = self.compo_name
        # add user values if any
        if conf_values is not None:
            for p in conf_values.keys():
                dico[p] = conf_values[p]

        # ask user for values
        for p in self.parameters:
            tp = TParam(p, self.compo_name, dico)
            if tp.name in dico:
                continue
            
            val = ""
            while not tp.check_value(val):
                val = input(tp.prompt)
                if len(val) == 0 and len(tp.default) > 0:
                    val = tp.default
            dico[tp.name] = val

        # ask for missing value for pyconf
        pyconfparam = self.get_pyconf_parameters()
        for p in filter(lambda l: not (l in dico), pyconfparam):
            rep = ""
            while len(rep) == 0:
                rep = input("%s? " % p)
            dico[p] = rep

        self.dico = dico
        return self.dico

def search_template(config, template):
    # search template
    template_src_dir = ""
    if os.path.isabs(template):
        if os.path.exists(template):
            template_src_dir = template
    else:
        # look in template directory
        for td in [os.path.join(config.VARS.datadir, "templates")]:
            zz = os.path.join(td, template)
            if os.path.exists(zz):
                template_src_dir = zz
                break

    if len(template_src_dir) == 0:
        raise src.SatException(_("Template not found: %s") % template)

    return template_src_dir
##
# Prepares a module from a template.
def prepare_from_template(config,
                          name,
                          template,
                          target_dir,
                          conf_values,
                          logger):
    template_src_dir = search_template(config, template)
    res = 0

    # copy the template
    if os.path.isfile(template_src_dir):
        logger.write("  " + _(
                        "Extract template %s\n") % src.printcolors.printcInfo(
                                                                   template), 4)
        src.system.archive_extract(template_src_dir, target_dir)
    else:
        logger.write("  " + _(
                        "Copy template %s\n") % src.printcolors.printcInfo(
                                                                   template), 4)
        shutil.copytree(template_src_dir, target_dir)
    logger.write("\n", 5)

    compo_name = name
    if name.endswith("CPP"):
        compo_name = name[:-3]

    # read settings
    settings_file = os.path.join(target_dir, "template.info")
    if not os.path.exists(settings_file):
        raise src.SatException(_("Settings file not found"))
    tsettings = TemplateSettings(compo_name, settings_file, target_dir)

    # first rename the files
    logger.write("  " + src.printcolors.printcLabel(_("Rename files\n")), 4)
    for root, dirs, files in os.walk(target_dir):
        for fic in files:
            ff = fic.replace(tsettings.file_subst, compo_name)
            if ff != fic:
                if os.path.exists(os.path.join(root, ff)):
                    raise src.SatException(_(
                        "Destination file already exists: %s") % os.path.join(
                                                                      root, ff))
                logger.write("    %s -> %s\n" % (fic, ff), 5)
                os.rename(os.path.join(root, fic), os.path.join(root, ff))

    # rename the directories
    logger.write("\n", 5)
    logger.write("  " + src.printcolors.printcLabel(_("Rename directories\n")),
                 4)
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for rep in dirs:
            dd = rep.replace(tsettings.file_subst, compo_name)
            if dd != rep:
                if os.path.exists(os.path.join(root, dd)):
                    raise src.SatException(_(
                                "Destination directory "
                                "already exists: %s") % os.path.join(root, dd))
                logger.write("    %s -> %s\n" % (rep, dd), 5)
                os.rename(os.path.join(root, rep), os.path.join(root, dd))

    # ask for missing parameters
    logger.write("\n", 5)
    logger.write("  " + src.printcolors.printcLabel(
                                        _("Make substitution in files\n")), 4)
    logger.write("    " + _("Delimiter =") + " %s\n" % tsettings.delimiter_char,
                 5)
    logger.write("    " + _("Ignore Filters =") + " %s\n" % ', '.join(
                                                   tsettings.ignore_filters), 5)
    dico = tsettings.get_parameters(conf_values)
    logger.write("\n", 3)

    # override standard string.Template class to use the desire delimiter
    class CompoTemplate(string.Template):
        delimiter = tsettings.delimiter_char

    # do substitution
    logger.write("\n", 5, True)
    pathlen = len(target_dir) + 1
    for root, dirs, files in os.walk(target_dir):
        for fic in files:
            fpath = os.path.join(root, fic)
            if not tsettings.check_file_for_substitution(fpath[pathlen:]):
                logger.write("  - %s\n" % fpath[pathlen:], 5)
                continue
            # read the file
            with open(fpath, 'r') as f:
                m = f.read()
                # make the substitution
                template = CompoTemplate(m)
                d = template.safe_substitute(dico)
                        
            changed = " "
            if d != m:
                changed = "*"
                with open(fpath, 'w') as f:
                    f.write(d)
            logger.write("  %s %s\n" % (changed, fpath[pathlen:]), 5)

    if not tsettings.has_pyconf:
        logger.write(src.printcolors.printcWarning(_(
                   "Definition for sat not found in settings file.")) + "\n", 2)
    else:
        definition = tsettings.pyconf % dico
        pyconf_file = os.path.join(target_dir, name + '.pyconf')
        f = open(pyconf_file, 'w')
        f.write(definition)
        f.close
        logger.write(_(
            "Create configuration file: ") + src.printcolors.printcInfo(
                                                         pyconf_file) + "\n", 2)

    if len(tsettings.post_command) > 0:
        cmd = tsettings.post_command % dico
        logger.write("\n", 5, True)
        logger.write(_(
              "Run post command: ") + src.printcolors.printcInfo(cmd) + "\n", 3)
        
        p = subprocess.Popen(cmd, shell=True, cwd=target_dir)
        p.wait()
        res = p.returncode

    return res

def get_template_info(config, template_name, logger):
    sources = search_template(config, template_name)
    src.printcolors.print_value(logger, _("Template"), sources)

    # read settings
    tmpdir = os.path.join(config.VARS.tmp_root, "tmp_template")
    settings_file = os.path.join(tmpdir, "template.info")
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    if os.path.isdir(sources):
        shutil.copytree(sources, tmpdir)
    else:
        src.system.archive_extract(sources, tmpdir)
        settings_file = os.path.join(tmpdir, "template.info")

    if not os.path.exists(settings_file):
        raise src.SatException(_("Settings file not found"))
    tsettings = TemplateSettings("NAME", settings_file, "target")
    
    logger.write("\n", 3)
    if len(tsettings.info) == 0:
        logger.write(src.printcolors.printcWarning(_(
                                       "No information for this template.")), 3)
    else:
        logger.write(tsettings.info, 3)

    logger.write("\n", 3)
    logger.write("= Configuration", 3)
    src.printcolors.print_value(logger,
                                "file substitution key",
                                tsettings.file_subst)
    src.printcolors.print_value(logger,
                                "subsitution key",
                                tsettings.delimiter_char)
    if len(tsettings.ignore_filters) > 0:
        src.printcolors.print_value(logger,
                                    "Ignore Filter",
                                    ', '.join(tsettings.ignore_filters))

    logger.write("\n", 3)
    logger.write("= Parameters", 3)
    pnames = []
    for pp in tsettings.parameters:
        tt = TParam(pp, "NAME")
        pnames.append(tt.name)
        src.printcolors.print_value(logger, "Name", tt.name)
        src.printcolors.print_value(logger, "Prompt", tt.raw_prompt)
        src.printcolors.print_value(logger, "Default value", tt.default)
        logger.write("\n", 3)

    retcode = 0
    logger.write("= Verification\n", 3)
    if tsettings.file_subst not in pnames:
        logger.write(
                     "file substitution key not defined as a "
                     "parameter: %s" % tsettings.file_subst, 3)
        retcode = 1
    
    reexp = tsettings.delimiter_char.replace("$", "\$") + "{(?P<name>\S[^}]*)"
    pathlen = len(tmpdir) + 1
    for root, __, files in os.walk(tmpdir):
        for fic in files:
            fpath = os.path.join(root, fic)
            if not tsettings.check_file_for_substitution(fpath[pathlen:]):
                continue
            # read the file
            with open(fpath, 'r') as f:
                m = f.read()
                zz = re.findall(reexp, m)
                zz = list(set(zz)) # reduce
                zz = filter(lambda l: l not in pnames, zz)
                if len(zz) > 0:
                    logger.write("Missing definition in %s: %s" % (
                        src.printcolors.printcLabel(
                                                fpath[pathlen:]), ", ".join(zz)), 3)
                    retcode = 1

    if retcode == 0:
        logger.write(src.printcolors.printc("OK"), 3)
    else:
        logger.write(src.printcolors.printc("KO"), 3)

    logger.write("\n", 3)

    # clean up tmp file
    shutil.rmtree(tmpdir)

    return retcode

##
# Describes the command
def description():
    return _("The template command creates the sources for a SALOME "
             "module from a template.\n\nexample\nsat template "
             "--name my_product_name --template PythonComponent --target /tmp")

def run(args, runner, logger):
    '''method that is called when salomeTools is called with template parameter.
    '''
    (options, args) = parser.parse_args(args)

    if options.template is None:
        msg = _("Error: the --%s argument is required\n") % "template"
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    if options.target is None and options.info is None:
        msg = _("Error: the --%s argument is required\n") % "target"
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    # if "APPLICATION" in runner.cfg:
    #     msg = _("Error: this command does not use a product.")
    #     logger.write(src.printcolors.printcError(msg), 1)
    #     logger.write("\n", 1)
    #     return 1

    if options.info:
        return get_template_info(runner.cfg, options.template, logger)

    if options.name is None:
        msg = _("Error: the --%s argument is required\n") % "name"
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    if not options.name.replace('_', '').isalnum():
        msg = _("Error: component name must contains only alphanumeric "
                "characters and no spaces\n")
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    if options.target is None:
        msg = _("Error: the --%s argument is required\n") % "target"
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1

    target_dir = os.path.join(options.target, options.name)
    if os.path.exists(target_dir):
        msg = _("Error: the target already exists: %s") % target_dir
        logger.write(src.printcolors.printcError(msg), 1)
        logger.write("\n", 1)
        return 1


    logger.write(_('Create sources from template\n'), 1)
    src.printcolors.print_value(logger, 'destination', target_dir, 2)
    src.printcolors.print_value(logger, 'name', options.name, 2)
    src.printcolors.print_value(logger, 'template', options.template, 2)
    logger.write("\n", 3, False)
    
    conf_values = None
    if options.param is not None:
        conf_values = {}
        for elt in options.param.split(","):
            param_def = elt.strip().split('=')
            if len(param_def) != 2:
                msg = _("Error: bad parameter definition")
                logger.write(src.printcolors.printcError(msg), 1)
                logger.write("\n", 1)
                return 1
            conf_values[param_def[0].strip()] = param_def[1].strip()
    
    retcode = prepare_from_template(runner.cfg, options.name, options.template,
        target_dir, conf_values, logger)

    if retcode == 0:
        logger.write(_(
                 "The sources were created in %s") % src.printcolors.printcInfo(
                                                                 target_dir), 3)
        logger.write(src.printcolors.printcWarning(_("\nDo not forget to put "
                                   "them in your version control system.")), 3)
        
    logger.write("\n", 3)
    
    return retcode
