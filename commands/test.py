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
import shutil
import subprocess
import datetime
import gzip

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

import src
import src.ElementTree as etree
from src.xmlManager import add_simple_node

# Define all possible option for the test command :  sat test <options>
parser = src.options.Options()
parser.add_option('a', 'appli', 'string', 'appli',
    _('Use this option to specify the path to an installed application.'))
parser.add_option('g', 'grid', 'string', 'grid',
    _("""Indicate the name of the grid to test.
\tThis name has to be registered in sat. If your test base is not known by sat, use the option --dir."""))
parser.add_option('m', 'module', 'list', 'modules',
    _('Indicate which module(s) to test (subdirectory of the grid).'))
parser.add_option('t', 'type', 'list', 'types',
    _('Indicate which type(s) to test (subdirectory of the module).'))
parser.add_option('d', 'dir', 'string', 'dir',
    _('Indicate the directory containing the test base.'), "")
parser.add_option('', 'mode', 'string', 'mode',
    _("Indicate which kind of test to run. If MODE is 'batch' only python and NO_GUI tests are run."), "normal")
parser.add_option('', 'display', 'string', 'display',
    _("""Set the display where to launch SALOME.
\tIf value is NO then option --show-desktop=0 will be used to launch SALOME."""))
parser.add_option('n', 'name', 'string', 'session',
    _('Give a name to the test session (REQUIRED if no product).'))
parser.add_option('', 'light', 'boolean', 'light',
    _('Only run minimal tests declared in TestsLight.txt.'), False)

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the test command description.
    :rtype: str
    '''
    return _("The test command runs a test base on a SALOME installation.")     

def parse_option(args, config):
    (options, args) = parser.parse_args(args)

    if not options.appli:
        options.appli = ""
    elif not os.path.isabs(options.appli):
        if not src.config_has_application(config):
            raise src.SatException(_("An application is required to use a "
                                     "relative path with option --appli"))
        options.appli = os.path.join(config.APPLICATION.workdir, options.appli)

        if not os.path.exists(options.appli):
            raise src.SatException(_("Application not found: %s") % 
                                   options.appli)

    return (options, args)

def ask_a_path():
    path = raw_input("enter a path where to save the result: ")
    if path == "":
        result = raw_input("the result will be not save. Are you sure to "
                           "continue ? [y/n] ")
        if result == "y":
            return path
        else:
            return ask_a_path()

    elif os.path.exists(path):
        result = raw_input("Warning, the content of %s will be deleted. Are you"
                           " sure to continue ? [y/n] " % path)
        if result == "y":
            return path
        else:
            return ask_a_path()
    else:
        return path

def save_file(filename, base):
    f = open(filename, 'r')
    content = f.read()
    f.close()

    objectname = sha1(content).hexdigest()

    f = gzip.open(os.path.join(base, '.objects', objectname), 'w')
    f.write(content)
    f.close()
    return objectname

def move_test_results(in_dir, what, out_dir, logger):
    if out_dir == in_dir:
        return

    finalPath = out_dir
    pathIsOk = False
    while not pathIsOk:
        try:
            # create test results directory if necessary
            #logger.write("FINAL = %s\n" % finalPath, 5)
            if not os.access(finalPath, os.F_OK):
                #shutil.rmtree(finalPath)
                os.makedirs(finalPath)
            pathIsOk = True
        except:
            logger.error(_("%s cannot be created.") % finalPath)
            finalPath = ask_a_path()

    if finalPath != "":
        os.makedirs(os.path.join(finalPath, what, 'BASES'))

        # check if .objects directory exists
        if not os.access(os.path.join(finalPath, '.objects'), os.F_OK):
            os.makedirs(os.path.join(finalPath, '.objects'))

        logger.write(_('copy tests results to %s ... ') % finalPath, 3)
        logger.flush()
        #logger.write("\n", 5)

        # copy env_info.py
        shutil.copy2(os.path.join(in_dir, what, 'env_info.py'),
                     os.path.join(finalPath, what, 'env_info.py'))

        # for all sub directory (ie grid) in the BASES directory
        for grid in os.listdir(os.path.join(in_dir, what, 'BASES')):
            outgrid = os.path.join(finalPath, what, 'BASES', grid)
            ingrid = os.path.join(in_dir, what, 'BASES', grid)

            # ignore files in root dir
            if not os.path.isdir(ingrid):
                continue

            os.makedirs(outgrid)
            #logger.write("  copy grid %s\n" % grid, 5)

            for module_ in [m for m in os.listdir(ingrid) if os.path.isdir(
                                                    os.path.join(ingrid, m))]:
                # ignore source configuration directories
                if module_[:4] == '.git' or module_ == 'CVS':
                    continue

                outmodule = os.path.join(outgrid, module_)
                inmodule = os.path.join(ingrid, module_)
                os.makedirs(outmodule)
                #logger.write("    copy module %s\n" % module_, 5)

                if module_ == 'RESSOURCES':
                    for file_name in os.listdir(inmodule):
                        if not os.path.isfile(os.path.join(inmodule,
                                                           file_name)):
                            continue
                        f = open(os.path.join(outmodule, file_name), "w")
                        f.write(save_file(os.path.join(inmodule, file_name),
                                          finalPath))
                        f.close()
                else:
                    for type_name in [t for t in os.listdir(inmodule) if 
                                      os.path.isdir(os.path.join(inmodule, t))]:
                        outtype = os.path.join(outmodule, type_name)
                        intype = os.path.join(inmodule, type_name)
                        os.makedirs(outtype)
                        
                        for file_name in os.listdir(intype):
                            if not os.path.isfile(os.path.join(intype,
                                                               file_name)):
                                continue
                            if file_name.endswith('result.py'):
                                shutil.copy2(os.path.join(intype, file_name),
                                             os.path.join(outtype, file_name))
                            else:
                                f = open(os.path.join(outtype, file_name), "w")
                                f.write(save_file(os.path.join(intype,
                                                               file_name),
                                                  finalPath))
                                f.close()

    logger.write(src.printcolors.printc("OK"), 3, False)
    logger.write("\n", 3, False)

def check_remote_machine(machine_name, logger):
    logger.write(_("\ncheck the display on %s\n" % machine_name), 4)
    ssh_cmd = 'ssh -o "StrictHostKeyChecking no" %s "ls"' % machine_name
    logger.write(_("Executing the command : %s " % ssh_cmd), 4)
    p = subprocess.Popen(ssh_cmd, 
                         shell=True,
                         stdin =subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        logger.write(src.printcolors.printc(src.KO_STATUS) + "\n", 1)
        logger.write("    " + src.printcolors.printcError(p.stderr.read()), 2)
        raise src.SatException("No ssh access to the display machine.")
    else:
        logger.write(src.printcolors.printcSuccess(src.OK_STATUS) + "\n\n", 4)

##
# Transform YYYYMMDD_hhmmss into YYYY-MM-DD hh:mm:ss.
def parse_date(date):
    if len(date) != 15:
        return date
    res = "%s-%s-%s %s:%s:%s" % (date[0:4], date[4:6], date[6:8], date[9:11], date[11:13], date[13:])
    return res

##
# Writes a report file from a XML tree.
def write_report(filename, xmlroot, stylesheet):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    f = open(filename, "w")
    f.write("<?xml version='1.0' encoding='utf-8'?>\n")
    if len(stylesheet) > 0:
        f.write("<?xml-stylesheet type='text/xsl' href='%s'?>\n" % stylesheet)
    f.write(etree.tostring(xmlroot, encoding='utf-8'))
    f.close()

##
# Creates the XML report for a product.
def create_test_report(config, dest_path, stylesheet, xmlname=""):
    application_name = config.VARS.application
    withappli = src.config_has_application(config)

    root = etree.Element("salome")
    prod_node = etree.Element("product", name=application_name, build=xmlname)
    root.append(prod_node)

    if withappli:

        add_simple_node(prod_node, "version_to_download", config.APPLICATION.name)
        
        add_simple_node(prod_node, "out_dir", config.APPLICATION.workdir)

    # add environment
    exec_node = add_simple_node(prod_node, "exec")
    exec_node.append(etree.Element("env", name="Host", value=config.VARS.node))
    exec_node.append(etree.Element("env", name="Architecture", value=config.VARS.dist))
    exec_node.append(etree.Element("env", name="Number of processors", value=str(config.VARS.nb_proc)))    
    exec_node.append(etree.Element("env", name="Begin date", value=parse_date(config.VARS.datehour)))
    exec_node.append(etree.Element("env", name="Command", value=config.VARS.command))
    exec_node.append(etree.Element("env", name="sat version", value=config.INTERNAL.sat_version))

    if 'TESTS' in config:
        tests = add_simple_node(prod_node, "tests")
        known_errors = add_simple_node(prod_node, "known_errors")
        new_errors = add_simple_node(prod_node, "new_errors")
        amend = add_simple_node(prod_node, "amend")
        tt = {}
        for test in config.TESTS:
            if not tt.has_key(test.grid):
                tt[test.grid] = [test]
            else:
                tt[test.grid].append(test)

        for grid in tt.keys():
            gn = add_simple_node(tests, "grid")
            gn.attrib['name'] = grid
            nb, nb_pass, nb_failed, nb_timeout, nb_not_run = 0, 0, 0, 0, 0
            modules = {}
            types = {}
            for test in tt[grid]:
                #print test.module
                if not modules.has_key(test.module):
                    mn = add_simple_node(gn, "module")
                    mn.attrib['name'] = test.module
                    modules[test.module] = mn

                if not types.has_key("%s/%s" % (test.module, test.type)):
                    tyn = add_simple_node(mn, "type")
                    tyn.attrib['name'] = test.type
                    types["%s/%s" % (test.module, test.type)] = tyn

                for script in test.script:
                    tn = add_simple_node(types["%s/%s" % (test.module, test.type)], "test")
                    #tn.attrib['grid'] = test.grid
                    #tn.attrib['module'] = test.module
                    tn.attrib['type'] = test.type
                    tn.attrib['script'] = script.name
                    if 'callback' in script:
                        try:
                            cnode = add_simple_node(tn, "callback")
                            if src.architecture.is_windows():
                                import string
                                cnode.text = filter(lambda x: x in string.printable,
                                                    script.callback)
                            else:
                                cnode.text = script.callback.decode('string_escape')
                        except UnicodeDecodeError as exc:
                            zz = script.callback[:exc.start] + '?' + script.callback[exc.end-2:]
                            cnode = add_simple_node(tn, "callback")
                            cnode.text = zz.decode("UTF-8")
                    if 'amend' in script:
                        cnode = add_simple_node(tn, "amend")
                        cnode.text = script.amend.decode("UTF-8")

                    if script.time < 0:
                        tn.attrib['exec_time'] = "?"
                    else:
                        tn.attrib['exec_time'] = "%.3f" % script.time
                    tn.attrib['res'] = script.res

                    if "amend" in script:
                        amend_test = add_simple_node(amend, "atest")
                        amend_test.attrib['name'] = os.path.join(test.module, test.type, script.name)
                        amend_test.attrib['reason'] = script.amend.decode("UTF-8")

                    # calculate status
                    nb += 1
                    if script.res == src.OK_STATUS: nb_pass += 1
                    elif script.res == src.TIMEOUT_STATUS: nb_timeout += 1
                    elif script.res == src.KO_STATUS: nb_failed += 1
                    else: nb_not_run += 1

                    if "known_error" in script:
                        kf_script = add_simple_node(known_errors, "error")
                        kf_script.attrib['name'] = os.path.join(test.module, test.type, script.name)
                        kf_script.attrib['date'] = script.known_error.date
                        kf_script.attrib['expected'] = script.known_error.expected
                        kf_script.attrib['comment'] = script.known_error.comment.decode("UTF-8")
                        kf_script.attrib['fixed'] = str(script.known_error.fixed)
                        overdue = datetime.datetime.today().strftime("%Y-%m-%d") > script.known_error.expected
                        if overdue:
                            kf_script.attrib['overdue'] = str(overdue)
                        
                    elif script.res == src.KO_STATUS:
                        new_err = add_simple_node(new_errors, "new_error")
                        script_path = os.path.join(test.module, test.type, script.name)
                        new_err.attrib['name'] = script_path
                        new_err.attrib['cmd'] = "sat testerror %s -s %s -c 'my comment' -p %s" % \
                            (application_name, script_path, config.VARS.dist)


            gn.attrib['total'] = str(nb)
            gn.attrib['pass'] = str(nb_pass)
            gn.attrib['failed'] = str(nb_failed)
            gn.attrib['timeout'] = str(nb_timeout)
            gn.attrib['not_run'] = str(nb_not_run)

    if len(xmlname) == 0:
        xmlname = application_name
    if not xmlname.endswith(".xml"):
        xmlname += ".xml"

    write_report(os.path.join(dest_path, xmlname), root, stylesheet)
    return src.OK_STATUS

def run(args, runner, logger):
    '''method that is called when salomeTools is called with test parameter.
    '''
    (options, args) = parse_option(args, runner.cfg)

    if options.grid and options.dir:
        raise src.SatException(_("The options --grid and --dir are not "
                                 "compatible!"))

    with_product = False
    if runner.cfg.VARS.application != 'None':
        logger.write(_('Running tests on application %s\n') % 
                            src.printcolors.printcLabel(
                                                runner.cfg.VARS.application), 1)
        with_product = True
    elif options.dir:
        logger.write(_('Running tests from directory %s\n') % 
                            src.printcolors.printcLabel(options.dir), 1)
    elif not options.grid:
        raise src.SatException(_('a grid or a directory is required'))

    if with_product:
        # check if environment is loaded
        if 'KERNEL_ROOT_DIR' in os.environ:
            logger.write(src.printcolors.printcWarning(_("WARNING: "
                            "SALOME environment already sourced")) + "\n", 1)
            
        
    elif options.appli:
        logger.write(src.printcolors.printcWarning(_("Running SALOME "
                                                "application.")) + "\n\n", 1)
    else:
        logger.write(src.printcolors.printcWarning(_("WARNING running "
                                            "without a product.")) + "\n\n", 1)

        # name for session is required
        if not options.session:
            raise src.SatException(_("--name argument is required when no "
                                        "product is specified."))

        # check if environment is loaded
        if not 'KERNEL_ROOT_DIR' in os.environ:
            raise src.SatException(_("SALOME environment not found") + "\n")

    # set the display
    show_desktop = (options.display and options.display.upper() == "NO")
    if options.display and options.display != "NO":
        remote_name = options.display.split(':')[0]
        if remote_name != "":
            check_remote_machine(remote_name, logger)
        # if explicitly set use user choice
        os.environ['DISPLAY'] = options.display
    elif 'DISPLAY' not in os.environ:
        # if no display set
        if 'display' in runner.cfg.SITE.test and len(runner.cfg.SITE.test.display) > 0:
            # use default value for test tool
            os.environ['DISPLAY'] = runner.cfg.SITE.test.display
        else:
            os.environ['DISPLAY'] = "localhost:0.0"

    # initialization
    #################
    if with_product:
        tmp_dir = runner.cfg.SITE.test.tmp_dir_with_product
    else:
        tmp_dir = runner.cfg.SITE.test.tmp_dir

    # remove previous tmp dir
    if os.access(tmp_dir, os.F_OK):
        try:
            shutil.rmtree(tmp_dir)
        except:
            logger.error(_("error removing TT_TMP_RESULT %s\n") 
                                % tmp_dir)

    lines = []
    lines.append("date = '%s'" % runner.cfg.VARS.date)
    lines.append("hour = '%s'" % runner.cfg.VARS.hour)
    lines.append("node = '%s'" % runner.cfg.VARS.node)
    lines.append("arch = '%s'" % runner.cfg.VARS.dist)

    if 'APPLICATION' in runner.cfg:
        lines.append("application_info = {}")
        lines.append("application_info['name'] = '%s'" % 
                     runner.cfg.APPLICATION.name)
        lines.append("application_info['tag'] = '%s'" % 
                     runner.cfg.APPLICATION.tag)
        lines.append("application_info['products'] = %s" % 
                     str(runner.cfg.APPLICATION.products))

    content = "\n".join(lines)

    # create hash from session information
    dirname = sha1(content).hexdigest()
    session_dir = os.path.join(tmp_dir, dirname)
    os.makedirs(session_dir)
    os.environ['TT_TMP_RESULT'] = session_dir

    # create env_info file
    f = open(os.path.join(session_dir, 'env_info.py'), "w")
    f.write(content)
    f.close()

    # create working dir and bases dir
    working_dir = os.path.join(session_dir, 'WORK')
    os.makedirs(working_dir)
    os.makedirs(os.path.join(session_dir, 'BASES'))
    os.chdir(working_dir)

    if 'PYTHONPATH' not in os.environ:
        os.environ['PYTHONPATH'] = ''
    else:
        for var in os.environ['PYTHONPATH'].split(':'):
            if var not in sys.path:
                sys.path.append(var)

    # launch of the tests
    #####################
    grid = ""
    if options.grid:
        grid = options.grid
    elif not options.dir and with_product and "test_base" in runner.cfg.APPLICATION:
        grid = runner.cfg.APPLICATION.test_base.name

    src.printcolors.print_value(logger, _('Display'), os.environ['DISPLAY'], 2)
    src.printcolors.print_value(logger, _('Timeout'),
                                runner.cfg.SITE.test.timeout, 2)
    if 'timeout_app' in runner.cfg.SITE.test:
        src.printcolors.print_value(logger, _('Timeout Salome'),
                                    runner.cfg.SITE.test.timeout_app, 2)
    src.printcolors.print_value(logger, _('Light mode'), options.light, 2)
    src.printcolors.print_value(logger, _("Working dir"), session_dir, 3)

    # create the test object
    test_runner = src.test_module.Test(runner.cfg,
                                  logger,
                                  session_dir,
                                  grid=grid,
                                  modules=options.modules,
                                  types=options.types,
                                  appli=options.appli,
                                  mode=options.mode,
                                  dir_=options.dir,
                                  show_desktop=show_desktop,
                                  light=options.light)
    
    # run the test
    logger.allowPrintLevel = False
    retcode = test_runner.run_all_tests(options.session)
    logger.allowPrintLevel = True

    logger.write(_("Tests finished"), 1)
    logger.write("\n", 2, False)
    
    logger.write(_("\nGenerate the specific test log\n"), 5)
    out_dir = os.path.join(runner.cfg.SITE.log.log_dir, "TEST")
    src.ensure_path_exists(out_dir)
    name_xml_board = logger.logFileName.split(".")[0] + "board" + ".xml"
    create_test_report(runner.cfg, out_dir, "test.xsl", xmlname = name_xml_board)
    xml_board_path = os.path.join(out_dir, name_xml_board)
    logger.l_logFiles.append(xml_board_path)
    logger.add_link(os.path.join("TEST", name_xml_board),
                    "board",
                    retcode,
                    "Click on the link to get the detailed test results")

    return retcode

