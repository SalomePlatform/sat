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

# Compatibility python 2/3 for input function
# input stays input for python 3 and input = raw_input for python 2
try:
    input = raw_input
except NameError:
    pass

verbose = False

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

import src
import src.ElementTree as etree
from src.xmlManager import add_simple_node

# Define all possible option for the test command :  sat test <options>
parser = src.options.Options()
parser.add_option('b', 'base', 'string', 'base',
    _("""Optional: The name of the test base to use."
          This name has to be registered in your application and in a project.
          A path to a test base can also be used."""))
parser.add_option('l', 'launcher', 'string', 'launcher',
    _("""Optional: Specify the path to a SALOME launcher
          used to launch the test scripts of the test base."""))
parser.add_option('g', 'grid', 'list', 'grids',
    _('Optional: Which grid(s) to test (subdirectory of the test base).'))
parser.add_option('s', 'session', 'list2', 'sessions',
    _('Optional: Which session(s) to test (subdirectory of the grid).'))
parser.add_option('', 'display', 'string', 'display',
    _("""Optional: Set the display where to launch SALOME.
          If value is NO then option --show-desktop=0 will be used to launch SALOME."""))
parser.add_option('', 'keep', 'boolean', 'keeptempdir',
                  _('Optional: keep temporary big tests directories.'))
def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the test command description.
    :rtype: str
    '''
    return _("The test command runs a test base on a SALOME installation.\n\n"
             "example:\nsat test SALOME-master --grid GEOM --session light")     

def parse_option_old(args, config):
    """ Parse the options and do some verifications about it
    
    :param args List: The list of arguments of the command
    :param config Config: The global configuration
    :return: the options of the current command launch and the full arguments
    :rtype: Tuple (options, args)
    """
    (options, args) = parser.parse_args(args)

    if not options.launcher:
        options.launcher = ""
    elif not os.path.isabs(options.launcher):
        if not src.config_has_application(config):
            msg = _("An application is required to use a relative path with option --appli")
            raise src.SatException(msg)
        options.launcher = os.path.join(config.APPLICATION.workdir,
                                        options.launcher)

        if not os.path.exists(options.launcher):
            raise src.SatException(_("Launcher not found: %s") % 
                                   options.launcher)

    return (options, args)


def parse_option(args, config):
    """ Parse the options and do some verifications about it

    :param args List: The list of arguments of the command
    :param config Config: The global configuration
    :return: the options of the current command launch and the full arguments
    :rtype: Tuple (options, args)
    """
    (options, args) = parser.parse_args(args)

    if not options.launcher:
        options.launcher = ""
        return (options, args)

    if not os.path.isabs(options.launcher):
        if not src.config_has_application(config):
            msg = _("An application is required to use a relative path with option --appli")
            raise src.SatException(msg)
        else:
            options.launcher = os.path.join(config.APPLICATION.workdir, options.launcher)
            if not os.path.exists(options.launcher):
                raise src.SatException(_("Launcher not found: %s") %  options.launcher)

    # absolute path
    launcher = os.path.realpath(os.path.expandvars(options.launcher))
    if os.path.exists(launcher):
        options.launcher = launcher
        return (options, args)

    raise src.SatException(_("Launcher not found: %s") %  options.launcher)


def ask_a_path():
    """ 
    """
    path = input("enter a path where to save the result: ")
    if path == "":
        result = input("the result will be not save. Are you sure to "
                           "continue ? [y/n] ")
        if result == "y":
            return path
        else:
            return ask_a_path()

    elif os.path.exists(path):
        result = input("Warning, the content of %s will be deleted. Are you"
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

        # for all sub directory (ie testbase) in the BASES directory
        for testbase in os.listdir(os.path.join(in_dir, what, 'BASES')):
            outtestbase = os.path.join(finalPath, what, 'BASES', testbase)
            intestbase = os.path.join(in_dir, what, 'BASES', testbase)

            # ignore files in root dir
            if not os.path.isdir(intestbase):
                continue

            os.makedirs(outtestbase)
            #logger.write("  copy testbase %s\n" % testbase, 5)

            for grid_ in [m for m in os.listdir(intestbase) \
                            if os.path.isdir(os.path.join(intestbase, m))]:
                # ignore source configuration directories
                if grid_[:4] == '.git' or grid_ == 'CVS':
                    continue

                outgrid = os.path.join(outtestbase, grid_)
                ingrid = os.path.join(intestbase, grid_)
                os.makedirs(outgrid)
                #logger.write("    copy grid %s\n" % grid_, 5)

                if grid_ == 'RESSOURCES':
                    for file_name in os.listdir(ingrid):
                        if not os.path.isfile(os.path.join(ingrid,
                                                           file_name)):
                            continue
                        f = open(os.path.join(outgrid, file_name), "w")
                        f.write(save_file(os.path.join(ingrid, file_name),
                                          finalPath))
                        f.close()
                else:
                    for session_name in [t for t in os.listdir(ingrid) if 
                                      os.path.isdir(os.path.join(ingrid, t))]:
                        outsession = os.path.join(outgrid, session_name)
                        insession = os.path.join(ingrid, session_name)
                        os.makedirs(outsession)
                        
                        for file_name in os.listdir(insession):
                            if not os.path.isfile(os.path.join(insession,
                                                               file_name)):
                                continue
                            if file_name.endswith('result.py'):
                                shutil.copy2(os.path.join(insession, file_name),
                                             os.path.join(outsession, file_name))
                            else:
                                f = open(os.path.join(outsession, file_name), "w")
                                f.write(save_file(os.path.join(insession,
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
        logger.write(src.printcolors.printcWarning((
                                    "No ssh access to the display machine.")),1)
    else:
        logger.write(src.printcolors.printcSuccess(src.OK_STATUS) + "\n\n", 4)

def findOrCreateNode(parentNode, nameNodeToFind):
    found = parentNode.find(nameNodeToFind)
    if found is None:
      created = add_simple_node(parentNode, nameNodeToFind)
      return created
    else:
      return found

def purgeEmptyNodes(root):
    """
    recursive remove node.text and node.tail if empty node
    as nothing else than whitespace(s) and RCLF(s)

    | this is comes from
    | 1) pretty print file xml -> creates indentation(s) in text and tail
    | 2) and reload parse file xml
    """
    # print("root", root.tag, root.text)
    text = root.text
    tail = root.tail
    if text is not None:
      if text.replace(" ", "").replace("\n", "") == "":
        # print("purgeEmptyNodes text %s" % root.tag)
        root.text = None
    if tail is not None:
      if tail.replace(" ", "").replace("\n", "") == "":
        # print("purgeEmptyNodes tail %s" % root.tag)
        root.tail = None
    for node in root:
      purgeEmptyNodes(node)
    return

##
# Creates the XML report for a product.
def create_test_report(config,
                       xml_history_path,
                       dest_path,
                       retcode,
                       xmlname=""):
    # get the date and hour of the launching of the command, in order to keep
    # history
    date_hour = config.VARS.datehour
    
    # Get some information to put in the xml file
    application_name = config.VARS.application
    withappli = src.config_has_application(config)
    
    first_time = False
    if not os.path.exists(xml_history_path):
        print("Log file creation %s" % xml_history_path)
        first_time = True
        root = etree.Element("salome")
        prod_node = etree.Element("product", name=application_name, build=xmlname)
        root.append(prod_node)
    else:
        print("Log file modification %s" % xml_history_path)
        root = etree.parse(xml_history_path).getroot()
        purgeEmptyNodes(root)
        prod_node = root.find("product")


    prod_node.attrib["history_file"] = os.path.basename(xml_history_path)
    prod_node.attrib["global_res"] = str(retcode)

    if withappli:
        if not first_time:
            for node in (prod_node.findall("version_to_download") + 
                         prod_node.findall("out_dir")):
                prod_node.remove(node)
                
        add_simple_node(prod_node, "version_to_download", config.APPLICATION.name)
        add_simple_node(prod_node, "out_dir", config.APPLICATION.workdir)

    # add environment
    if not first_time:
        for node in prod_node.findall("exec"):
            prod_node.remove(node)
        
    exec_node = add_simple_node(prod_node, "exec")
    exec_node.append(etree.Element("env", name="Host", value=config.VARS.node))
    exec_node.append(etree.Element("env", name="Architecture", value=config.VARS.dist))
    exec_node.append(etree.Element("env", name="Number of processors", value=str(config.VARS.nb_proc)))
    exec_node.append(etree.Element("env", name="Begin date", value=src.parse_date(date_hour)))
    exec_node.append(etree.Element("env", name="Command", value=config.VARS.command))
    exec_node.append(etree.Element("env", name="sat version", value=config.INTERNAL.sat_version))

    if 'TESTS' in config:
        tests = findOrCreateNode(prod_node, "tests")
        known_errors = findOrCreateNode(prod_node, "known_errors")
        new_errors = findOrCreateNode(prod_node, "new_errors")
        amend = findOrCreateNode(prod_node, "amend")
        
        tt = {}
        for test in config.TESTS:
            if not test.testbase in tt:
                tt[test.testbase] = [test]
            else:
                tt[test.testbase].append(test)
        
        for testbase in tt.keys():
            if verbose: print("---- create_test_report %s %s" % (testbase, first_time))
            gn = findOrCreateNode(tests, "testbase")

            # initialize all grids and session to "not executed"
            for mn in gn.findall("grid"):
                mn.attrib["executed_last_time"] = "no"
                for tyn in mn.findall("session"):
                    tyn.attrib["executed_last_time"] = "no"
                    for test_node in tyn.findall('test'):
                        for node in test_node.getchildren():
                            if node.tag != "history":
                                test_node.remove(node)

                        attribs_to_pop = []
                        for attribute in test_node.attrib:
                            if (attribute != "script" and
                                                    attribute != "res"):
                                attribs_to_pop.append(attribute)
                        for attribute in attribs_to_pop:
                            test_node.attrib.pop(attribute)
            
            gn.attrib['name'] = testbase
            nb, nb_pass, nb_failed, nb_timeout, nb_not_run = 0, 0, 0, 0, 0
            grids = {}
            sessions = {}
            for test in tt[testbase]:
                if not (test.grid in grids):
                    if first_time:
                        mn = add_simple_node(gn, "grid")
                        mn.attrib['name'] = test.grid
                    else:
                        l_mn = gn.findall("grid")
                        mn = None
                        for grid_node in l_mn:
                            if grid_node.attrib['name'] == test.grid:
                                mn = grid_node
                                break
                        if mn == None:
                            mn = add_simple_node(gn, "grid")
                            mn.attrib['name'] = test.grid
                    
                    grids[test.grid] = mn
                
                mn.attrib["executed_last_time"] = "yes"
                
                if not "%s/%s" % (test.grid, test.session) in sessions:
                    if first_time:
                        tyn = add_simple_node(mn, "session")
                        tyn.attrib['name'] = test.session
                    else:
                        l_tyn = mn.findall("session")
                        tyn = None
                        for session_node in l_tyn:
                            if session_node.attrib['name'] == test.session:
                                tyn = session_node
                                break
                        if tyn == None:
                            tyn = add_simple_node(mn, "session")
                            tyn.attrib['name'] = test.session
                        
                    sessions["%s/%s" % (test.grid, test.session)] = tyn

                tyn.attrib["executed_last_time"] = "yes"

                for script in test.script:
                    if first_time:
                        tn = add_simple_node(sessions[
                                           "%s/%s" % (test.grid, test.session)],
                                             "test")
                        tn.attrib['session'] = test.session
                        tn.attrib['script'] = script.name
                        hn = add_simple_node(tn, "history")
                    else:
                        l_tn = sessions["%s/%s" % (test.grid, test.session)].findall(
                                                                         "test")
                        tn = None
                        for test_node in l_tn:
                            if test_node.attrib['script'] == script['name']:
                                tn = test_node
                                break
                        
                        if tn == None:
                            tn = add_simple_node(sessions[
                                           "%s/%s" % (test.grid, test.session)],
                                             "test")
                            tn.attrib['session'] = test.session
                            tn.attrib['script'] = script.name
                            hn = add_simple_node(tn, "history")
                        else:
                            # Get or create the history node for the current test
                            if len(tn.findall("history")) == 0:
                                hn = add_simple_node(tn, "history")
                            else:
                                hn = tn.find("history")
                            # Put the last test data into the history
                            if 'res' in tn.attrib:
                                attributes = {"date_hour" : date_hour,
                                              "res" : tn.attrib['res'] }
                                add_simple_node(hn,
                                                "previous_test",
                                                attrib=attributes)
                            for node in tn:
                                if node.tag != "history":
                                    tn.remove(node)
                    
                    if 'callback' in script:
                        try:
                            cnode = add_simple_node(tn, "callback")
                            if True:  # bug xml mal forme colorisation  src.architecture.is_windows():
                                import string
                                cnode.text = filter(
                                                lambda x: x in string.printable,
                                                script.callback)
                            else:
                                cnode.text = script.callback.decode(
                                                                'string_escape')
                        except UnicodeDecodeError as exc:
                            zz = (script.callback[:exc.start] +
                                  '?' +
                                  script.callback[exc.end-2:])
                            cnode = add_simple_node(tn, "callback")
                            cnode.text = zz.decode("UTF-8")
                    
                    # Add the script content
                    cnode = add_simple_node(tn, "content")
                    cnode.text = script.content
                    
                    # Add the script execution log
                    cnode = add_simple_node(tn, "out")
                    cnode.text = script.out
                    
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
                        amend_test.attrib['name'] = os.path.join(test.grid,
                                                                 test.session,
                                                                 script.name)
                        amend_test.attrib['reason'] = script.amend.decode(
                                                                        "UTF-8")

                    # calculate status
                    nb += 1
                    if script.res == src.OK_STATUS: nb_pass += 1
                    elif script.res == src.TIMEOUT_STATUS: nb_timeout += 1
                    elif script.res == src.KO_STATUS: nb_failed += 1
                    else: nb_not_run += 1

                    if "known_error" in script:
                        kf_script = add_simple_node(known_errors, "error")
                        kf_script.attrib['name'] = os.path.join(test.grid,
                                                                test.session,
                                                                script.name)
                        kf_script.attrib['date'] = script.known_error.date
                        kf_script.attrib[
                                    'expected'] = script.known_error.expected
                        kf_script.attrib[
                         'comment'] = script.known_error.comment.decode("UTF-8")
                        kf_script.attrib['fixed'] = str(
                                                       script.known_error.fixed)
                        overdue = datetime.datetime.today().strftime("%Y-%m-"
                                            "%d") > script.known_error.expected
                        if overdue:
                            kf_script.attrib['overdue'] = str(overdue)
                        
                    elif script.res == src.KO_STATUS:
                        new_err = add_simple_node(new_errors, "new_error")
                        script_path = os.path.join(test.grid,
                                                   test.session, script.name)
                        new_err.attrib['name'] = script_path
                        new_err.attrib['cmd'] = ("sat testerror %s -s %s -c 'my"
                                                 " comment' -p %s" % \
                            (application_name, script_path, config.VARS.dist))


            gn.attrib['total'] = str(nb)
            gn.attrib['pass'] = str(nb_pass)
            gn.attrib['failed'] = str(nb_failed)
            gn.attrib['timeout'] = str(nb_timeout)
            gn.attrib['not_run'] = str(nb_not_run)
            
            # Remove the res attribute of all tests that were not launched 
            # this time
            for mn in gn.findall("grid"):
                if mn.attrib["executed_last_time"] == "no":
                    for tyn in mn.findall("session"):
                        if tyn.attrib["executed_last_time"] == "no":
                            for test_node in tyn.findall('test'):
                                if "res" in test_node.attrib:
                                    test_node.attrib.pop("res")          
    
    if len(xmlname) == 0:
        xmlname = application_name
    if not xmlname.endswith(".xml"):
        xmlname += ".xml"

    src.xmlManager.write_report(os.path.join(dest_path, xmlname), root, "test.xsl")
    src.xmlManager.write_report(xml_history_path, root, "test_history.xsl")
    return src.OK_STATUS

def generate_history_xml_path(config, test_base):
    """Generate the name of the xml file that contain the history of the tests
       on the machine with the current APPLICATION and the current test base.
    
    :param config Config: The global configuration
    :param test_base Str: The test base name (or path)
    :return: the full path of the history xml file
    :rtype: Str
    """
    history_xml_name = ""
    if "APPLICATION" in config:
        history_xml_name += config.APPLICATION.name
        history_xml_name += "-" 
    history_xml_name += config.VARS.dist
    history_xml_name += "-"
    test_base_name = test_base
    if os.path.exists(test_base):
        test_base_name = os.path.basename(test_base)
    history_xml_name += test_base_name
    history_xml_name += ".xml"
    log_dir = src.get_log_path(config)
    return os.path.join(log_dir, "TEST", history_xml_name)

def run(args, runner, logger):
    '''method that is called when salomeTools is called with test parameter.
    '''
    (options, args) = parse_option(args, runner.cfg)

    # the test base is specified either by the application, or by the --base option
    with_application = False
    if runner.cfg.VARS.application != 'None':
        logger.write(_('Running tests on application %s\n') % 
                            src.printcolors.printcLabel(
                                                runner.cfg.VARS.application), 1)
        with_application = True
    elif not options.base:
        raise src.SatException(_('A test base is required. Use the --base '
                                 'option'))

    # the launcher is specified either by the application, or by the --launcher option
    if with_application:
        # check if environment is loaded
        if 'KERNEL_ROOT_DIR' in os.environ:
            logger.write(src.printcolors.printcWarning(_("WARNING: "
                            "SALOME environment already sourced")) + "\n", 1)
            
        
    elif options.launcher:
        logger.write(src.printcolors.printcWarning(_("Running SALOME "
                                                "application.")) + "\n\n", 1)
    else:
        msg = _("Impossible to find any launcher.\nPlease specify an "
                "application or a launcher")
        logger.write(src.printcolors.printcError(msg))
        logger.write("\n")
        return 1

    # set the display
    show_desktop = (options.display and options.display.upper() == "NO")
    if options.display and options.display != "NO":
        remote_name = options.display.split(':')[0]
        if remote_name != "" and (not src.architecture.is_windows()):
            check_remote_machine(remote_name, logger)
        # if explicitly set use user choice
        os.environ['DISPLAY'] = options.display
    elif 'DISPLAY' not in os.environ:
        # if no display set
        if ('test' in runner.cfg.LOCAL and
                'display' in runner.cfg.LOCAL.test and 
                len(runner.cfg.LOCAL.test.display) > 0):
            # use default value for test tool
            os.environ['DISPLAY'] = runner.cfg.LOCAL.test.display
        else:
            os.environ['DISPLAY'] = "localhost:0.0"

    # initialization
    #################
    if with_application:
        tmp_dir = os.path.join(runner.cfg.VARS.tmp_root,
                               runner.cfg.APPLICATION.name,
                               "test")
    else:
        tmp_dir = os.path.join(runner.cfg.VARS.tmp_root,
                               "test")

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

    # create hash from context information
    # CVW TODO or not dirname = datetime.datetime.now().strftime("%y%m%d_%H%M%S_") + sha1(content.encode()).hexdigest()[0:8]
    dirname = sha1(content.encode()).hexdigest()[0:8] # only 8 firsts probably good
    base_dir = os.path.join(tmp_dir, dirname)
    os.makedirs(base_dir)
    os.environ['TT_TMP_RESULT'] = base_dir

    # create env_info file
    with open(os.path.join(base_dir, 'env_info.py'), "w") as f:
        f.write(content)

    # create working dir and bases dir
    working_dir = os.path.join(base_dir, 'WORK')
    os.makedirs(working_dir)
    os.makedirs(os.path.join(base_dir, 'BASES'))
    os.chdir(working_dir)

    if 'PYTHONPATH' not in os.environ:
        os.environ['PYTHONPATH'] = ''
    else:
        for var in os.environ['PYTHONPATH'].split(':'):
            if var not in sys.path:
                sys.path.append(var)

    # launch of the tests
    #####################
    test_base = ""
    if options.base:
        test_base = options.base
    elif with_application and "test_base" in runner.cfg.APPLICATION:
        test_base = runner.cfg.APPLICATION.test_base.name

    src.printcolors.print_value(logger, _('Display'), os.environ['DISPLAY'], 2)
    src.printcolors.print_value(logger, _('Timeout'),
                                src.test_module.DEFAULT_TIMEOUT, 2)
    src.printcolors.print_value(logger, _("Working dir"), base_dir, 3)

    # create the test object
    test_runner = src.test_module.Test(runner.cfg,
                                  logger,
                                  base_dir,
                                  testbase=test_base,
                                  grids=options.grids,
                                  sessions=options.sessions,
                                  launcher=options.launcher,
                                  show_desktop=show_desktop)
    
    if not test_runner.test_base_found:
        # Fail 
        return 1
        
    # run the test
    logger.allowPrintLevel = False
    retcode = test_runner.run_all_tests()
    logger.allowPrintLevel = True

    logger.write(_("Tests finished"), 1)
    logger.write("\n", 2, False)
    
    logger.write(_("\nGenerate the specific test log\n"), 5)
    log_dir = src.get_log_path(runner.cfg)
    out_dir = os.path.join(log_dir, "TEST")
    src.ensure_path_exists(out_dir)
    name_xml_board = logger.logFileName.split(".")[0] + "_board.xml"
    historic_xml_path = generate_history_xml_path(runner.cfg, test_base)
    
    create_test_report(runner.cfg,
                       historic_xml_path,
                       out_dir,
                       retcode,
                       xmlname = name_xml_board)
    xml_board_path = os.path.join(out_dir, name_xml_board)

    logger.l_logFiles.append(xml_board_path)
    logger.add_link(os.path.join("TEST", name_xml_board),
                    "board",
                    retcode,
                    "Click on the link to get the detailed test results")
    logger.write("\nTests board file %s\n" % xml_board_path, 1)

    # Add the historic files into the log files list of the command
    logger.l_logFiles.append(historic_xml_path)

    if not options.keeptempdir:
      logger.write("Removing the temporary directory: rm -rf %s\n" % test_runner.tmp_working_dir, 5)
      if os.path.exists(test_runner.tmp_working_dir):
        shutil.rmtree(test_runner.tmp_working_dir)
    else:
      logger.write("NOT Removing the temporary directory: rm -rf %s\n" % test_runner.tmp_working_dir, 5)

    return retcode

