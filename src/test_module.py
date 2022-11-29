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

# Python 2/3 compatibility for execfile function
try:
    execfile
except:
    def execfile(somefile, global_vars, local_vars):
        with open(somefile) as f:
            code = compile(f.read(), somefile, 'exec')
            exec(code, global_vars, local_vars)

import os
import sys
import datetime
import shutil
import string
import imp
import subprocess
import glob
import pprint as PP

verbose = False

from . import fork
import src
from  src.versionMinorMajorPatch import MinorMajorPatch as MMP

# directories not considered as test grids
C_IGNORE_GRIDS = ['.git', '.svn', 'RESSOURCES']

DEFAULT_TIMEOUT = 150

# Get directory to be used for the temporary files.
#
def getTmpDirDEFAULT():
    if src.architecture.is_windows():
        directory = os.getenv("TEMP")
    else:
        # for Linux: use /tmp/logs/{user} folder
        directory = os.path.join( '/tmp', 'logs', os.getenv("USER", "unknown"))
    return directory

class Test:
    def __init__(self,
                 config,
                 logger,
                 tmp_working_dir,
                 testbase="",
                 grids=None,
                 sessions=None,
                 launcher="",
                 show_desktop=True):
        self.grids = grids
        self.config = config
        self.logger = logger
        self.tmp_working_dir = tmp_working_dir
        self.sessions = sessions
        self.launcher = launcher
        self.show_desktop = show_desktop

        res = self.prepare_testbase(testbase)
        self.test_base_found = True
        if res == 1:
            # Fail
            self.test_base_found = False

        self.settings = {}
        self.known_errors = None

        # create section for results
        self.config.TESTS = src.pyconf.Sequence(self.config)

        self.nb_run = 0
        self.nb_succeed = 0
        self.nb_timeout = 0
        self.nb_not_run = 0
        self.nb_acknoledge = 0

    def _copy_dir(self, source, target):
        if self.config.VARS.python >= "2.6":
            shutil.copytree(source, target,
                            symlinks=True,
                            ignore=shutil.ignore_patterns('.git*','.svn*'))
        else:
            shutil.copytree(source, target,
                            symlinks=True)

    def prepare_testbase_from_dir(self, testbase_name, testbase_dir):
        self.logger.write(_("get test base from dir: %s\n") % \
                          src.printcolors.printcLabel(testbase_dir), 3)
        if not os.access(testbase_dir, os.X_OK):
            raise src.SatException(_("testbase %(name)s (%(dir)s) does not "
                                     "exist ...\n") % { 'name': testbase_name,
                                                       'dir': testbase_dir })

        self._copy_dir(testbase_dir,
                       os.path.join(self.tmp_working_dir, 'BASES', testbase_name))

    def prepare_testbase_from_git(self,
                                  testbase_name,
                                  testbase_base,
                                  testbase_tag):
        self.logger.write(
            _("get test base '%(testbase)s' with '%(tag)s' tag from git\n") % {
                        "testbase" : src.printcolors.printcLabel(testbase_name),
                        "tag" : src.printcolors.printcLabel(testbase_tag)},
                          3)
        try:
            def set_signal(): # pragma: no cover
                """see http://bugs.python.org/issue1652"""
                import signal
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)

            cmd = "git clone --depth 1 %(base)s %(dir)s"
            cmd += " && cd %(dir)s"
            if testbase_tag=='master':
                cmd += " && git fetch origin %(branch)s"
            else:
                cmd += " && git fetch origin %(branch)s:%(branch)s"
            cmd += " && git checkout %(branch)s"
            cmd = cmd % { 'branch': testbase_tag,
                         'base': testbase_base,
                         'dir': testbase_name }

            self.logger.write("> %s\n" % cmd, 5)
            if src.architecture.is_windows():
                # preexec_fn not supported on windows platform
                res = subprocess.call(cmd,
                                cwd=os.path.join(self.tmp_working_dir, 'BASES'),
                                shell=True,
                                stdout=self.logger.logTxtFile,
                                stderr=subprocess.PIPE)
            else:
                res = subprocess.call(cmd,
                                cwd=os.path.join(self.tmp_working_dir, 'BASES'),
                                shell=True,
                                preexec_fn=set_signal,
                                stdout=self.logger.logTxtFile,
                                stderr=subprocess.PIPE)
            if res != 0:
                raise src.SatException(_("Error: unable to get test base "
                                         "'%(name)s' from git '%(repo)s'.") % \
                                       { 'name': testbase_name,
                                        'repo': testbase_base })

        except OSError:
            self.logger.error(_("git is not installed. exiting...\n"))
            sys.exit(0)

    def prepare_testbase_from_svn(self, user, testbase_name, testbase_base):
        self.logger.write(_("get test base '%s' from svn\n") % \
                          src.printcolors.printcLabel(testbase_name), 3)
        try:
            def set_signal(): # pragma: no cover
                """see http://bugs.python.org/issue1652"""
                import signal
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)

            cmd = "svn checkout --username %(user)s %(base)s %(dir)s"
            cmd = cmd % { 'user': user,
                         'base': testbase_base,
                         'dir': testbase_name }

            # Get the application environment
            self.logger.write(_("Set the application environment\n"), 5)
            env_appli = src.environment.SalomeEnviron(self.config,
                                      src.environment.Environ(dict(os.environ)))
            env_appli.set_application_env(self.logger)

            self.logger.write("> %s\n" % cmd, 5)
            if src.architecture.is_windows():
                # preexec_fn not supported on windows platform
                res = subprocess.call(cmd,
                                cwd=os.path.join(self.tmp_working_dir, 'BASES'),
                                shell=True,
                                stdout=self.logger.logTxtFile,
                                stderr=subprocess.PIPE)
            else:
                res = subprocess.call(cmd,
                                cwd=os.path.join(self.tmp_working_dir, 'BASES'),
                                shell=True,
                                preexec_fn=set_signal,
                                stdout=self.logger.logTxtFile,
                                stderr=subprocess.PIPE,
                                env=env_appli.environ.environ,)

            if res != 0:
                raise src.SatException(_("Error: unable to get test base '%(nam"
                                         "e)s' from svn '%(repo)s'.") % \
                                       { 'name': testbase_name,
                                        'repo': testbase_base })

        except OSError:
            self.logger.error(_("svn is not installed. exiting...\n"))
            sys.exit(0)

    ##
    # Configure tests base.
    def prepare_testbase(self, test_base_name):
        src.printcolors.print_value(self.logger,
                                    _("Test base"),
                                    test_base_name,
                                    3)
        self.logger.write("\n", 3, False)

        # search for the test base
        test_base_info = None
        for project_name in self.config.PROJECTS.projects:
            project_info = self.config.PROJECTS.projects[project_name]
            if "test_bases" not in project_info:
                continue
            for t_b_info in project_info.test_bases:
                if t_b_info.name == test_base_name:
                    test_base_info = t_b_info

        if not test_base_info:
            if os.path.exists(test_base_name):
                self.prepare_testbase_from_dir("DIR", test_base_name)
                self.currentTestBase = "DIR"
                return 0

        if not test_base_info:
            message = (_("########## ERROR: test base '%s' not found\n") %
                       test_base_name)
            self.logger.write("%s\n" % src.printcolors.printcError(message))
            return 1

        if test_base_info.get_sources == "dir":
            self.prepare_testbase_from_dir(test_base_name,
                                           test_base_info.info.dir)
        elif test_base_info.get_sources == "git":
            self.prepare_testbase_from_git(test_base_name,
                                       test_base_info.info.base,
                                       self.config.APPLICATION.test_base.tag)
        elif test_base_info.get_sources == "svn":
            svn_user = src.get_cfg_param(test_base_info.info,
                                         "svn_user",
                                         self.config.USER.svn_user)
            self.prepare_testbase_from_svn(svn_user,
                                       test_base_name,
                                       test_base_info.info.base)
        else:
            raise src.SatException(_("unknown source type '%(type)s' for test b"
                                     "ase '%(base)s' ...\n") % {
                                        'type': test_base_info.get_sources,
                                        'base': test_base_name })

        self.currentTestBase = test_base_name

    ##
    # Searches if the script is declared in known errors pyconf.
    # Update the status if needed.
    def search_known_errors(self, status, test_grid, test_session, test):
        test_path = os.path.join(test_grid, test_session, test)
        if not src.config_has_application(self.config):
            return status, []

        if self.known_errors is None:
            return status, []

        platform = self.config.VARS.arch
        application = self.config.VARS.application
        error = self.known_errors.get_error(test_path, application, platform)
        if error is None:
            return status, []

        if status == src.OK_STATUS:
            if not error.fixed:
                # the error is fixed
                self.known_errors.fix_error(error)
                #import testerror
                #testerror.write_test_failures(
                #                        self.config.TOOLS.testerror.file_path,
                #                        self.known_errors.errors)
            return status, [ error.date,
                            error.expected,
                            error.comment,
                            error.fixed ]

        if error.fixed:
            self.known_errors.unfix_error(error)
            #import testerror
            #testerror.write_test_failures(self.config.TOOLS.testerror.file_path,
            #                              self.known_errors.errors)

        delta = self.known_errors.get_expecting_days(error)
        kfres = [ error.date, error.expected, error.comment, error.fixed ]
        if delta < 0:
            return src.KO_STATUS, kfres
        return src.KNOWNFAILURE_STATUS, kfres

    ##
    # Read the *.result.py files.
    def read_results(self, listTest, has_timed_out):
        results = {}
        for test in listTest:
            resfile = os.path.join(self.currentDir,
                                   self.currentgrid,
                                   self.currentsession,
                                   test[:-3] + ".result.py")

            # check if <test>.result.py file exists
            if not os.path.exists(resfile):
                results[test] = ["?", -1, "", []]
            else:
                gdic, ldic = {}, {}
                if verbose:
                  print("test script: '%s':\n'%s'\n" % (resfile, open(resfile, 'r').read()))

                try:
                  execfile(resfile, gdic, ldic)

                  status = src.TIMEOUT_STATUS
                  if not has_timed_out:
                      status = src.KO_STATUS

                  if 'status' in ldic:
                      status = ldic['status']

                  expected = []
                  if status == src.KO_STATUS or status == src.OK_STATUS:
                      status, expected = self.search_known_errors(status,
                                                              self.currentgrid,
                                                              self.currentsession,
                                                              test)

                  callback = ""
                  if 'callback' in ldic:
                      callback = ldic['callback']
                  elif status == src.KO_STATUS:
                      callback = "CRASH"
                      if verbose:
                        print("--- CRASH ldic\n%s" % PP.pformat(ldic)) # cvw TODO
                        print("--- CRASH gdic\n%s" %  PP.pformat(gdic))
                        pass

                  exec_time = -1
                  if 'time' in ldic:
                      try:
                          exec_time = float(ldic['time'])
                      except:
                          pass

                  results[test] = [status, exec_time, callback, expected]

                except:
                  results[test] = ["?", -1, "", []]
                  # results[test] = [src.O_STATUS, -1, open(resfile, 'r').read(), []]

            # check if <test>.py file exists
            testfile = os.path.join(self.currentDir,
                                   self.currentgrid,
                                   self.currentsession,
                                   test)

            if not os.path.exists(testfile):
                results[test].append('')
            else:
                text = open(testfile, "r").read()
                results[test].append(text)

            # check if <test>.out.py file exists
            outfile = os.path.join(self.currentDir,
                                   self.currentgrid,
                                   self.currentsession,
                                   test[:-3] + ".out.py")

            if not os.path.exists(outfile):
                results[test].append('')
            else:
                text = open(outfile, "r").read()
                results[test].append(text)

        return results

    ##
    # Generates the script to be run by Salome.
    # This python script includes init and close statements and a loop
    # calling all the scripts of a single directory.
    def generate_script(self, listTest, script_path, ignoreList):
        # open template file
        tFile = os.path.join(self.config.VARS.srcDir, "test", "scriptTemplate.py")
        with open(tFile, 'r') as f:
          template = string.Template(f.read())

        # create substitution dictionary
        d = dict()
        d['resourcesWay'] = os.path.join(self.currentDir, 'RESSOURCES')
        d['tmpDir'] = os.path.join(self.tmp_working_dir, 'WORK')
        d['toolsWay'] = os.path.join(self.config.VARS.srcDir, "test")
        d['sessionDir'] = os.path.join(self.currentDir, self.currentgrid, self.currentsession)
        d['resultFile'] = os.path.join(self.tmp_working_dir, 'WORK', 'exec_result')
        d['listTest'] = listTest
        d['sessionName'] = self.currentsession
        d['ignore'] = ignoreList

        # create script with template
        contents = template.safe_substitute(d)
        if verbose: print("generate_script '%s':\n%s" % (script_path, contents)) # cvw TODO
        with open(script_path, 'w') as f:
          f.write(contents)


    # Find the getTmpDir function that gives access to *_pidict file directory.
    # (the *_pidict file exists when SALOME is launched)
    def get_tmp_dir(self):
        # Rare case where there is no KERNEL in grid list
        # (for example MED_STANDALONE)
        if ('APPLICATION' in self.config
                and 'KERNEL' not in self.config.APPLICATION.products
                and 'KERNEL_ROOT_DIR' not in os.environ):
            return getTmpDirDEFAULT

        # Case where "sat test" is launched in an existing SALOME environment
        if 'KERNEL_ROOT_DIR' in os.environ:
            root_dir =  os.environ['KERNEL_ROOT_DIR']

        if ('APPLICATION' in self.config and
            'KERNEL' in self.config.APPLICATION.products):
            root_dir = src.product.get_product_config(self.config, "KERNEL").install_dir

        # Case where there the appli option is called (with path to launcher)
        if len(self.launcher) > 0:
            # There are two cases : The old application (runAppli)
            # and the new one
            launcherName = os.path.basename(self.launcher)
            launcherDir = os.path.dirname(self.launcher)
            if launcherName == 'runAppli':
                # Old application
                cmd = """
for i in %s/env.d/*.sh;
  do source ${i};
done
echo $KERNEL_ROOT_DIR
""" % launcherDir
            else:
                # New application
                cmd = """
echo -e 'import os\nprint(os.environ[\"KERNEL_ROOT_DIR\"])' > tmpscript.py
%s shell tmpscript.py
""" % self.launcher

            if src.architecture.is_windows():
                subproc_res = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            shell=True).communicate()
                pass
            else:
                subproc_res = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            shell=True,
                            executable='/bin/bash').communicate()
                pass

            root_dir = subproc_res[0].split()[-1]

        # import grid salome_utils from KERNEL that gives
        # the right getTmpDir function
        root_dir = root_dir.decode('utf-8')
        aPath = [os.path.join(root_dir, 'bin', 'salome')]
        sal_uts = "salome_utils"
        try:
            (file_, pathname, description) = imp.find_module(sal_uts, aPath )
        except Exception:
            msg = "inexisting %s.py in %s" % (sal_uts, aPath)
            raise Exception(msg)

        try:
            grid = imp.load_module(sal_uts, file_, pathname, description)
            return grid.getLogDir
        except:
            grid = imp.load_module(sal_uts, file_, pathname, description)
            return grid.getTmpDir
        finally:
            if file_:
                file_.close()


    def get_test_timeout(self, test_name, default_value):
        if ("timeout" in self.settings and
                test_name in self.settings["timeout"]):
            return self.settings["timeout"][test_name]

        return default_value

    def generate_launching_commands(self):

        # Case where there the appli option is called (with path to launcher)
        if len(self.launcher) > 0:
            # There are two cases : The old application (runAppli)
            # and the new one
            launcherName = os.path.basename(self.launcher)
            launcherDir = os.path.dirname(self.launcher)
            if os.path.basename(launcherDir) == 'APPLI':
                # Old application
                binSalome = self.launcher
                binPython = ("for i in " +
                             launcherDir +
                             "/env.d/*.sh; do source ${i}; done ; python")
                killSalome = ("for i in " +
                        launcherDir +
                        "/env.d/*.sh; do source ${i}; done ; killSalome.py'")
                return binSalome, binPython, killSalome
            else:
                # New application
                binSalome = self.launcher
                binPython = self.launcher + ' shell'
                killSalome = self.launcher + ' killall'
                return binSalome, binPython, killSalome

        # SALOME version detection and APPLI repository detection
        VersionSalome = src.get_salome_version(self.config)
        appdir = 'APPLI'
        if "APPLI" in self.config and "application_name" in self.config.APPLI:
            appdir = self.config.APPLI.application_name

        # Case where SALOME has NOT the launcher that uses the SalomeContext API
        if VersionSalome < MMP([7,3,0]):
            binSalome = os.path.join(self.config.APPLICATION.workdir,
                                     appdir,
                                     "runAppli")
            binPython = "python"
            killSalome = "killSalome.py"
            src.environment.load_environment(self.config, False, self.logger)
            return binSalome, binPython, killSalome

        # Case where SALOME has the launcher that uses the SalomeContext API
        else:
            launcher_name = src.get_launcher_name(self.config)
            binSalome = os.path.join(self.config.APPLICATION.workdir,
                                     launcher_name)

            binPython = binSalome + ' shell'
            killSalome = binSalome + ' killall'
            return binSalome, binPython, killSalome

        return binSalome, binPython, killSalome


    ##
    # Runs tests of a session (using a single instance of Salome).
    def run_tests(self, listTest, ignoreList):
        out_path = os.path.join(self.currentDir,
                                self.currentgrid,
                                self.currentsession)
        if verbose: print("run_tests '%s'\nlistTest: %s\nignoreList: %s" %
                   (self.currentDir, PP.pformat(listTest), PP.pformat(ignoreList))) # cvw TODO
        sessionname = "%s/%s" % (self.currentgrid, self.currentsession)
        time_out = self.get_test_timeout(sessionname,
                                         DEFAULT_TIMEOUT)

        time_out_salome = DEFAULT_TIMEOUT

        # generate wrapper script
        script_path = os.path.join(out_path, 'wrapperScript.py')
        self.generate_script(listTest, script_path, ignoreList)

        tmpDir = self.get_tmp_dir()

        binSalome, binPython, killSalome = self.generate_launching_commands()
        if "run_with_grids" in self.settings and \
           sessionname in self.settings["run_with_grids"]:
            binSalome = (binSalome + " -m %s" % self.settings["run_with_grids"][sessionname])

        logWay = os.path.join(self.tmp_working_dir, "WORK", "log_cxx")

        status = False
        elapsed = -1
        if self.currentsession.startswith("NOGUI_"):
            # runSalome -t (bash)
            status, elapsed = fork.batch(
                                binSalome,
                                self.logger,
                                os.path.join(self.tmp_working_dir, "WORK"),
                                [ "-t", "--shutdown-server=1", script_path ],
                                delai=time_out,
                                log=logWay)

        elif self.currentsession.startswith("PY_"):
            # python script.py
            status, elapsed = fork.batch(
                                binPython,
                                self.logger,
                                os.path.join(self.tmp_working_dir, "WORK"),
                                [script_path],
                                delai=time_out,
                                log=logWay)

        else:
            opt = "-z 0"
            if self.show_desktop: opt = "--show-desktop=0"
            status, elapsed = fork.batch_salome(
                                binSalome,
                                self.logger,
                                os.path.join( self.tmp_working_dir, "WORK"),
                                [ opt, "--shutdown-server=1", script_path ],
                                getTmpDir=tmpDir,
                                fin=killSalome,
                                delai=time_out,
                                log=logWay,
                                delaiapp=time_out_salome)

        self.logger.write("status = %s, elapsed = %s\n" % (status, elapsed), 5)

        # create the test result to add in the config object
        test_info = src.pyconf.Mapping(self.config)
        test_info.testbase = self.currentTestBase
        test_info.grid = self.currentgrid
        test_info.session = self.currentsession
        test_info.script = src.pyconf.Sequence(self.config)

        script_results = self.read_results(listTest, elapsed == time_out)
        for sr in sorted(script_results.keys()):
            self.nb_run += 1

            # create script result
            script_info = src.pyconf.Mapping(self.config)
            script_info.name = sr
            script_info.res = script_results[sr][0]
            script_info.time = script_results[sr][1]
            if script_info.res == src.TIMEOUT_STATUS:
                script_info.time = time_out
            if script_info.time < 1e-3: script_info.time = 0

            callback = script_results[sr][2]
            if script_info.res != src.OK_STATUS and len(callback) > 0:
                script_info.callback = callback

            kfres = script_results[sr][3]
            if len(kfres) > 0:
                script_info.known_error = src.pyconf.Mapping(self.config)
                script_info.known_error.date = kfres[0]
                script_info.known_error.expected = kfres[1]
                script_info.known_error.comment = kfres[2]
                script_info.known_error.fixed = kfres[3]

            script_info.content = script_results[sr][4]
            script_info.out = script_results[sr][5]

            # add it to the list of results
            test_info.script.append(script_info, '')

            # display the results
            if script_info.time > 0:
                exectime = "(%7.3f s)" % script_info.time
            else:
                exectime = ""

            sp = "." * (35 - len(script_info.name))
            self.logger.write(self.write_test_margin(3), 3)
            self.logger.write("script %s %s %s %s\n" % (
                                src.printcolors.printcLabel(script_info.name),
                                sp,
                                src.printcolors.printc(script_info.res),
                                exectime), 3, False)
            if script_info and len(callback) > 0:
                self.logger.write("Exception in %s\n%s\n" % \
                    (script_info.name,
                     src.printcolors.printcWarning(callback)), 2, False)

            if script_info.res == src.OK_STATUS:
                self.nb_succeed += 1
            elif script_info.res == src.KNOWNFAILURE_STATUS:
                self.nb_acknoledge += 1
            elif script_info.res == src.TIMEOUT_STATUS:
                self.nb_timeout += 1
            elif script_info.res == src.NA_STATUS:
                self.nb_run -= 1
            elif script_info.res == "?":
                self.nb_not_run += 1


        self.config.TESTS.append(test_info, '')

    ##
    # Runs all tests of a session.
    def run_session_tests(self):

        self.logger.write(self.write_test_margin(2), 3)
        self.logger.write("Session = %s\n" % src.printcolors.printcLabel(
                                                    self.currentsession), 3, False)

        # prepare list of tests to run
        tests = os.listdir(os.path.join(self.currentDir,
                                        self.currentgrid,
                                        self.currentsession))
        # avoid result files of previous tests, if presents
        # tests = filter(lambda l: l.endswith(".py"), tests)
        tests = [t for t in tests if t.endswith(".py") \
                   and not ( t.endswith(".out.py") or \
                             t.endswith(".result.py") or \
                             t.endswith("wrapperScript.py") \
                           ) ]
        tests = sorted(tests, key=str.lower)

        # build list of known failures
        cat = "%s/%s/" % (self.currentgrid, self.currentsession)
        ignoreDict = {}
        for k in self.ignore_tests.keys():
            if k.startswith(cat):
                ignoreDict[k[len(cat):]] = self.ignore_tests[k]

        self.run_tests(tests, ignoreDict)

    ##
    # Runs all tests of a grid.
    def run_grid_tests(self):
        self.logger.write(self.write_test_margin(1), 3)
        self.logger.write("grid = %s\n" % src.printcolors.printcLabel(
                                                self.currentgrid), 3, False)

        grid_path = os.path.join(self.currentDir, self.currentgrid)

        sessions = []
        if self.sessions is not None:
            sessions = self.sessions # user choice
        else:
            # use all scripts in grid
            sessions = filter(lambda l: l not in C_IGNORE_GRIDS,
                           os.listdir(grid_path))
            sessions = filter(lambda l: os.path.isdir(os.path.join(grid_path,
                                                                l)), sessions)

        sessions = sorted(sessions, key=str.lower)
        existingSessions = self.getSubDirectories(grid_path)
        for session_ in sessions:
            if not os.path.exists(os.path.join(grid_path, session_)):
                self.logger.write(self.write_test_margin(2), 3)
                msg = """\
Session '%s' not found
Existing sessions are:
%s
""" % (session_, PP.pformat(sorted(existingSessions)))
                self.logger.write(src.printcolors.printcWarning(msg), 3, False)
            else:
                self.currentsession = session_
                self.run_session_tests()

    def getSubDirectories(self, aDir):
        """
        get names of first level of sub directories in aDir
        excluding '.git' etc as beginning with '.'
        """
        res = os.listdir(aDir)
        res = [d for d in res if os.path.isdir(os.path.join(aDir, d)) and d[0] != '.']
        # print("getSubDirectories %s are:\n%s" % (aDir, PP.pformat(res)))
        return res

    ##
    # Runs test testbase.
    def run_testbase_tests(self):
        res_dir = os.path.join(self.currentDir, "RESSOURCES")
        os.environ['PYTHONPATH'] =  (res_dir +
                                     os.pathsep +
                                     os.environ['PYTHONPATH'])
        os.environ['TT_BASE_RESSOURCES'] = res_dir
        src.printcolors.print_value(self.logger,
                                    "TT_BASE_RESSOURCES",
                                    res_dir,
                                    4)
        self.logger.write("\n", 4, False)

        self.logger.write(self.write_test_margin(0), 3)
        testbase_label = "Test base = %s\n" % src.printcolors.printcLabel(
                                                        self.currentTestBase)
        self.logger.write(testbase_label, 3, False)
        self.logger.write("-" * len(src.printcolors.cleancolor(testbase_label)),
                          3)
        self.logger.write("\n", 3, False)

        # load settings
        settings_file = os.path.join(res_dir, "test_settings.py")
        if os.path.exists(settings_file):
            gdic, ldic = {}, {}
            execfile(settings_file, gdic, ldic)
            self.logger.write("Load test settings '%s'\n" % settings_file, 5)
            self.settings = ldic['settings_dic']
            self.ignore_tests = ldic['known_failures_list']
            if isinstance(self.ignore_tests, list):
                self.ignore_tests = {}
                self.logger.write(src.printcolors.printcWarning(
                  "known_failures_list must be a dictionary (not a list)") + "\n", 1, False)
        else:
            self.ignore_tests = {}
            self.settings.clear()

        # read known failures pyconf
        if "testerror" in self.config.LOCAL:
            #import testerror
            #self.known_errors = testerror.read_test_failures(
            #                            self.config.TOOLS.testerror.file_path,
            #                            do_error=False)
            pass
        else:
            self.known_errors = None

        if self.grids is not None:
            grids = self.grids # given by user
        else:
            # select all the grids (i.e. directories) in the directory
            grids = filter(lambda l: l not in C_IGNORE_GRIDS,
                             os.listdir(self.currentDir))
            grids = filter(lambda l: os.path.isdir(
                                        os.path.join(self.currentDir, l)),
                             grids)

        grids = sorted(grids, key=str.lower)
        existingGrids = self.getSubDirectories(self.currentDir)
        for grid in grids:
            if not os.path.exists(os.path.join(self.currentDir, grid)):
                self.logger.write(self.write_test_margin(1), 3)
                msg = """\
Grid '%s' does not exist
Existing grids are:
%s
""" % (grid, PP.pformat(sorted(existingGrids)))
                self.logger.write(src.printcolors.printcWarning(msg), 3, False)
            else:
                self.currentgrid = grid
                self.run_grid_tests()

    def run_script(self, script_name):
        if ('APPLICATION' in self.config and
                script_name in self.config.APPLICATION):
            script = self.config.APPLICATION[script_name]
            if len(script) == 0:
                return

            self.logger.write("\n", 2, False)
            if not os.path.exists(script):
                self.logger.write(src.printcolors.printcWarning("WARNING: scrip"
                                        "t not found: %s" % script) + "\n", 2)
            else:
                self.logger.write(src.printcolors.printcHeader("----------- sta"
                                            "rt %s" % script_name) + "\n", 2)
                self.logger.write("Run script: %s\n" % script, 2)
                subprocess.Popen(script, shell=True).wait()
                self.logger.write(src.printcolors.printcHeader("----------- end"
                                                " %s" % script_name) + "\n", 2)

    def run_all_tests(self):
        initTime = datetime.datetime.now()

        self.run_script('test_setup')
        self.logger.write("\n", 2, False)

        self.logger.write(src.printcolors.printcHeader(
                                            _("=== STARTING TESTS")) + "\n", 2)
        self.logger.write("\n", 2, False)
        self.currentDir = os.path.join(self.tmp_working_dir,
                                       'BASES',
                                       self.currentTestBase)
        self.run_testbase_tests()

        # calculate total execution time
        totalTime = datetime.datetime.now() - initTime
        totalTime -= datetime.timedelta(microseconds=totalTime.microseconds)
        self.logger.write("\n", 2, False)
        self.logger.write(src.printcolors.printcHeader(_("=== END TESTS")), 2)
        self.logger.write(" %s\n" % src.printcolors.printcInfo(str(totalTime)),
                          2,
                          False)

        #
        # Start the tests
        #
        self.run_script('test_cleanup')
        self.logger.write("\n", 2, False)

        # evaluate results

        res_out = _("Tests Results: %(succeed)d / %(total)d\n") % \
            { 'succeed': self.nb_succeed, 'total': self.nb_run }
        if self.nb_succeed == self.nb_run:
            res_out = src.printcolors.printcSuccess(res_out)
        else:
            res_out = src.printcolors.printcError(res_out)
        self.logger.write(res_out, 1)

        if self.nb_timeout > 0:
            self.logger.write(_("%d tests TIMEOUT\n") % self.nb_timeout, 1)
        if self.nb_not_run > 0:
            self.logger.write(_("%d tests not executed\n") % self.nb_not_run, 1)
        if self.nb_acknoledge > 0:
            self.logger.write(_("%d tests known failures\n") % self.nb_acknoledge, 1)

        status = src.OK_STATUS
        if self.nb_run - self.nb_succeed - self.nb_acknoledge > 0:
            status = src.KO_STATUS
        elif self.nb_acknoledge:
            status = src.KNOWNFAILURE_STATUS

        self.logger.write(_("Status: %s\n" % status), 3)

        return self.nb_run - self.nb_succeed - self.nb_acknoledge

    ##
    # Write margin to show test results.
    def write_test_margin(self, tab):
        if tab == 0:
            return ""
        return "|   " * (tab - 1) + "+ "
