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

'''
In this file : all functions that do a system call, 
like open a browser or an editor, or call a git command
'''

import os
import sys
import shlex
import shutil
import subprocess as SP
import time
import tarfile


import src
import src.debug as DBG
import src.utilsSat as UTS

from . import printcolors

def _darwin_viewer(command, filePath=""):
    '''macOS: the default viewers of the sat user configuration (firefox,
    evince) are usually not in PATH (applications live in /Applications).
    If the program of command is not found, "open" is used instead: it opens
    the file with the default application (browser, Preview...), or with the
    default text editor ("open -t") for the other files (pyconf, rst...).

    :param command str: The viewer command (may contain %s).
    :param filePath str: The file(s) to open.
    :return: command, or an "open" command if its program is not in PATH
    :rtype: str
    '''
    try:
        words = shlex.split(command) if command else []
    except ValueError:
        words = command.split()
    if words and shutil.which(words[0]):
        return command
    if str(filePath).lower().endswith((".pdf", ".html", ".htm", ".xml")):
        return "open"
    return "open -t"

def show_in_editor(editor, filePath, logger):
    '''open filePath using editor.

    :param editor str: The editor to use.
    :param filePath str: The path to the file to open.
    '''
    # default editor is vi
    if editor is None or len(editor) == 0:
        editor = 'vi'
    elif src.architecture.is_darwin():
        # browser or pdf viewer (sat doc) not in PATH -> open
        editor = _darwin_viewer(editor, filePath)

    if '%s' not in editor:
        editor += ' %s'

    try:
        # launch cmd using subprocess.Popen
        cmd = editor % filePath
        logger.write('Launched command:\n' + cmd + '\n', 5)
        p = SP.Popen(cmd, shell=True)
        p.communicate()
    except Exception:
        logger.write(printcolors.printcError(_("Unable to edit file %s\n") 
                                             % filePath), 1)

def show_in_webbrowser(editor, filePath, logger):
    '''open filePath using web browser firefox, chromium etc...
    if file is xml, previous http sever is done before to fix new security problems
    
    :param editor str: The web browser to use.
    :param filePath str: The path to the file to open.
    '''
    import psutil
    darwin = src.architecture.is_darwin()
    # default editor is firefox (macOS: default browser if not in PATH)
    if editor is None or len(editor) == 0:
        editor = 'firefox'
    if darwin:
        editor = _darwin_viewer(editor, ".html")

    path, namefile = os.path.split(filePath)
    basefile, ext = os.path.splitext(namefile)

    # macOS: /usr/bin/python3 is the Xcode stub (may ask to install the
    # Command Line Tools): use the Python running sat
    python = shlex.quote(sys.executable) if darwin else "python3"

    # previouly http.server 8765/6/7... kill ... or not ? TODO wait and see REX
    port = os.getenv('SAT_PORT_LOG', '8765')
    for proc in psutil.process_iter():
      # help(proc)
      # macOS: reading the command line of a process of another user
      # (or of a zombie) raises AccessDenied/ZombieProcess
      try:
        cmdline = " ".join(proc.cmdline())
      except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        continue
      if "-m http.server %s" % port in cmdline:
        print("kill previous process '%s'" % cmdline)
        try:
          proc.kill()  # TODO may be not owner ? -> change 8766/7/8... as SAT_PORT_LOG
        except (psutil.AccessDenied, psutil.NoSuchProcess):
          pass

    # "open" returns at once: wait for the server before opening the page
    wait_server = "sleep 1" if darwin else ""
    cmd = """
set -x
cd "%(path)s"
%(python)s -m http.server %(port)s > /dev/null 2>&1 &
%(wait_server)s
%(editor)s http://localhost:%(port)s/%(namefile)s
""" % {"path": path, "editor": editor, "namefile": namefile, 'port': port,
       "python": python, "wait_server": wait_server}

    # print("show_in_webbrowser:\n%s" % cmd)
    
    try:
        # launch cmd using subprocess.Popen
        logger.write('Launched command:\n%s\n' % cmd, 5)
        p = SP.Popen(cmd, shell=True, stdout=SP.PIPE, stderr=SP.STDOUT)
        res_out, _ = p.communicate()   # _ = None as stderr=SP.STDOUT
        # print("Launched command stdout:\n%s" % res_out)
    except Exception as e:
        logger.write(printcolors.printcError(_("Unable to display file %s\n%s\n") 
                                             % (filePath, e)), 1)
    

def git_describe(repo_path):
    '''Use git describe --tags command to return tag description of the git repository"
    :param repo_path str: The git repository to describe
    '''
    git_cmd="cd %s;git describe --tags" % repo_path
    p = SP.Popen(git_cmd, shell=True, stdin=SP.PIPE, stdout=SP.PIPE, stderr=SP.PIPE)
    p.wait()
    if p.returncode != 0:
        return False
    else:
        tag_description=p.stdout.readlines()[0].strip()
        # with python3 this utf8 bytes should be decoded
        if isinstance(tag_description, bytes):
            tag_description=tag_description.decode("utf-8", "ignore")
        return tag_description

def _touch_last_commit_cmd():
    '''shell line that sets the modification date of %(where)s to the date
    of the last commit of the repository %(where_git)s.

    GNU touch: -d "2026-10-01 12:34:56 +0200" (git %ai, "date_format" is
    replaced by "%ai" in git_extract).
    macOS: the BSD touch -d only accepts YYYY-MM-DDThh:mm:SS, and rejects the
    space and the time zone of %ai: touch -t CCYYMMDDhhmm.SS is used, with the
    commit date converted to the local time (same as touch -t).
    '''
    if src.architecture.is_darwin():
        return ("touch -t \"$(git --git-dir=%(where_git)s log -1 "
                "--date=format-local:%Y%m%d%H%M.%S --format=%ad)\" %(where)s")
    return ("touch -d \"$(git --git-dir=%(where_git)s  log -1 "
            "--format=date_format)\" %(where)s")

def git_extract(from_what, tag, git_options, git_commands, where, logger, environment=None):
  '''Extracts sources from a git repository.
87
  :param from_what str: The remote git repository.
  :param tag str: The tag.
  :param git_options str: git options
  :param git_commands array: git command lines
  :param where str: The path where to extract.
  :param logger Logger: The logger instance to use.
  :param environment src.environment.Environ: The environment to source when extracting.
  :return: True if the extraction is successful
  :rtype: boolean
  '''
  DBG.write("git_extract", [from_what, tag, str(where)])
  if not where.exists():
    where.make()
  where_git = os.path.join(str(where), ".git")
  if tag == "master" or tag == "HEAD":
    if src.architecture.is_windows():
      cmd = "git clone %(git_options)s %(remote)s %(where)s"
      if len(git_commands) > 0:
        cmd+= "&&" + "cd %(where)s"
        for git_command in git_commands:
          cmd+= "&&" + git_command
    else:
      cmd = "\n" + "set -x"
      cmd+= "\n" + "git clone %(git_options)s %(remote)s %(where)s"
      cmd+= "\n" + "if [ $? -ne 0 ]; then"
      cmd+= "\n" + "  exit 1"
      cmd+= "\n" + "fi"
      cmd+= "\n" + _touch_last_commit_cmd()
      cmd+= "\n" + "if [ $? -ne 0 ]; then"
      cmd+= "\n" + "  exit 1"
      cmd+= "\n" + "fi"
      if len(git_commands) > 0:
        cmd+= "\n" + "cd %(where)s"
        for git_command in git_commands:
            cmd+= "\n" + git_command
            cmd+= "\n" + "if [ $? -ne 0 ]; then"
            cmd+= "\n" + "  exit 1"
            cmd+= "\n" + "fi"
  else:
    if src.architecture.is_windows():
      cmd = "rmdir /S /Q %(where)s"
      cmd+= "&&" + "git clone %(git_options)s %(remote)s %(where)s"
      cmd+= "&&" + "git --git-dir=%(where_git)s --work-tree=%(where)s checkout %(tag)s"
      if len(git_commands) > 0:
        cmd+= "&&" + "cd %(where)s"
        for git_command in git_commands:
          cmd+= "&&" + git_command
    else:
      cmd = "\n" + "set -x"
      cmd+= "\n" + "git clone %(git_options)s %(remote)s %(where)s"
      cmd+= "\n" + "if [ $? -ne 0 ]; then"
      cmd+= "\n" + "  exit 1"
      cmd+= "\n" + "fi"
      cmd+= "\n" + "git --git-dir=%(where_git)s --work-tree=%(where)s checkout %(tag)s"
      cmd+= "\n" + "if [ $? -ne 0 ]; then"
      cmd+= "\n" + "  exit 1"
      cmd+= "\n" + "fi"
      if len(git_commands) > 0:
        cmd+= "\n" + "cd %(where)s"
        for git_command in git_commands:
            cmd+= "\n" + git_command
            cmd+= "\n" + "if [ $? -ne 0 ]; then"
            cmd+= "\n" + "  exit 1"
            cmd+= "\n" + "fi"
      cmd+= "\n" + "git --git-dir=%(where_git)s status | grep HEAD"
      cmd+= "\n" + _touch_last_commit_cmd()
      cmd+= "\n" + "exit 0"
  aDict = {'%(git_options)s': git_options,
           '%(remote)s'   : from_what,
           '%(where)s'    : str(where),
           '%(tag)s'      : tag,
           '%(where_git)s': where_git
           }
  for k, v in aDict.items():
      cmd= cmd.replace(k,v)
  cmd=cmd.replace('date_format', '"%ai"')
  logger.logTxtFile.write("\n" + cmd + "\n")
  logger.logTxtFile.flush()
  DBG.write("cmd", cmd)
  # git commands may fail sometimes for various raisons 
  # (big module, network troubles, tuleap maintenance)
  # therefore we give several tries
  i_try = 0
  max_number_of_tries = 3
  sleep_delay = 30  # seconds
  while (True):
    i_try += 1
    rc = UTS.Popen(cmd, cwd=str(where.dir()), env=environment.environ.environ, logger=logger)
    if rc.isOk() or (i_try>=max_number_of_tries):
      break
    logger.write('\ngit command failed! Wait %d seconds and give an other try (%d/%d)\n' % \
                 (sleep_delay, i_try + 1, max_number_of_tries), 3)
    time.sleep(sleep_delay) # wait a little

  return rc.isOk()


def git_extract_sub_dir(from_what, tag, git_options, git_commands, where, sub_dir, logger, environment=None):
  '''Extracts sources from a subtree sub_dir of a git repository.

  :param from_what str: The remote git repository.
  :param tag str: The tag.
  :param git_options str: git options
  :param git_commands array: git command lines
  :param where str: The path where to extract.
  :param sub_dir str: The relative path of subtree to extract.
  :param logger Logger: The logger instance to use.
  :param environment src.environment.Environ: The environment to source when extracting.
  :return: True if the extraction is successful
  :rtype: boolean
  '''
  strWhere = str(where)
  tmpWhere = strWhere + '_tmp'
  parentWhere = os.path.dirname(strWhere)
  if not os.path.exists(parentWhere):
    logger.error("not existing directory: %s" % parentWhere)
    return False
  if os.path.isdir(strWhere):
    logger.error("do not override existing directory: %s" % strWhere)
    return False
  aDict = {'%(git_options)s': git_options,
           '%(remote)s'     : from_what,
           '%(tag)s'        : tag,
           '%(sub_dir)s'    : sub_dir,
           '%(where)s'      : strWhere,
           '%(parentWhere)s': parentWhere,
           '%(tmpWhere)s'   : tmpWhere
           }
  DBG.write("git_extract_sub_dir", aDict)
  if not src.architecture.is_windows():
    cmd = "\n" + "set -x"
    cmd+= "\n" + "export tmpDir=%(tmpWhere)s"
    cmd+= "\n" + "rm -rf $tmpDir"
    cmd+= "\n" + "git clone %(git_options)s %(remote)s $tmpDir"
    cmd+= "\n" + "if [ $? -ne 0 ]; then"
    cmd+= "\n" + "  exit 1"
    cmd+= "\n" + "fi"
    cmd+= "\n" + "cd $tmpDir"
    cmd+= "\n" + "git checkout %(tag)s"
    cmd+= "\n" + "if [ $? -ne 0 ]; then"
    cmd+= "\n" + "  exit 1"
    cmd+= "\n" + "fi"
    if len(git_commands) > 0:
      for git_command in git_commands:
        cmd+= "\n" + git_command
        cmd+= "\n" + "if [ $? -ne 0 ]; then"
        cmd+= "\n" + "  exit 1"
        cmd+= "\n" + "fi"
    cmd+= "\n" + "mv %(sub_dir)s %(where)s"
    cmd+= "\n" + "git log -1 > %(where)s/README_git_log.txt"
    cmd+= "\n" + "if [ $? -ne 0 ]; then"
    cmd+= "\n" + "  exit 1"
    cmd+= "\n" + "fi"
    cmd+= "\n" + "rm -rf ${tmpDir}"
  else:
    cmd+=        "set tmpDir=%(tmpWhere)s"
    cmd+= "&&" + "rmdir /S /Q %tmpDir%"
    cmd+= "&&" + "git clone %(git_options)s %(remote)s %tmpDir%"
    cmd+= "&&" + "cd %tmpDir%"
    cmd+= "&&" + "git checkout %(tag)s"
    if len(git_commands) > 0:
      for git_command in git_commands:
        cmd+= "&&" + git_command
    cmd+= "&&" + "mv %(sub_dir)s %(where)s"
    cmd+= "&&" + "git log -1 > %(where)s\\README_git_log.txt"
    cmd+= "&&" + "rmdir /S /Q %tmpDir%"

  for k, v in aDict.items():
      cmd= cmd.replace(k,v)
  DBG.write("cmd", cmd)

  for nbtry in range(0,3): # retries case of network problem
    rc = UTS.Popen(cmd, cwd=parentWhere, env=environment.environ.environ, logger=logger)
    if rc.isOk(): break
    time.sleep(30) # wait a little

  return rc.isOk()

def archive_extract(from_what, where, logger):
    '''Extracts sources from an archive.
    
    :param from_what str: The path to the archive.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :return: True if the extraction is successful
    :rtype: boolean
    '''
    try:
        archive = tarfile.open(from_what)
        for i in archive.getmembers():
            archive.extract(i, path=str(where))
        return True, os.path.commonprefix(archive.getnames())
    except Exception as exc:
        logger.write("archive_extract: %s\n" % exc)
        return False, None

def cvs_extract(protocol, user, server, base, tag, product, where,
                logger, checkout=False, environment=None):
    '''Extracts sources from a cvs repository.
    
    :param protocol str: The cvs protocol.
    :param user str: The user to be used.
    :param server str: The remote cvs server.
    :param base str: .
    :param tag str: The tag.
    :param product str: The product.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :param checkout boolean: If true use checkout cvs.
    :param environment src.environment.Environ: The environment to source when
                                                extracting.
    :return: True if the extraction is successful
    :rtype: boolean
    '''

    opttag = ''
    if tag is not None and len(tag) > 0:
        opttag = '-r ' + tag

    cmd = 'export'
    if checkout:
        cmd = 'checkout'
    elif len(opttag) == 0:
        opttag = '-DNOW'
    
    if len(protocol) > 0:
        root = "%s@%s:%s" % (user, server, base)
        command = "cvs -d :%(protocol)s:%(root)s %(command)s -d %(where)s %(tag)s %(product)s" % \
            { 'protocol': protocol, 'root': root, 'where': str(where.base()),
              'tag': opttag, 'product': product, 'command': cmd }
    else:
        command = "cvs -d %(root)s %(command)s -d %(where)s %(tag)s %(base)s/%(product)s" % \
            { 'root': server, 'base': base, 'where': str(where.base()),
              'tag': opttag, 'product': product, 'command': cmd }

    logger.write(command + "\n", 5)

    if not where.dir().exists():
        where.dir().make()

    logger.logTxtFile.write("\n" + command + "\n")
    logger.logTxtFile.flush()        
    res = SP.call(command, cwd=str(where.dir()),
                           env=environment.environ.environ,
                           shell=True,
                           stdout=logger.logTxtFile,
                           stderr=SP.STDOUT)
    return (res == 0)

def svn_extract(user,
                from_what,
                tag,
                where,
                logger,
                checkout=False,
                environment=None):
    '''Extracts sources from a svn repository.
    
    :param user str: The user to be used.
    :param from_what str: The remote git repository.
    :param tag str: The tag.
    :param where str: The path where to extract.
    :param logger Logger: The logger instance to use.
    :param checkout boolean: If true use checkout svn.
    :param environment src.environment.Environ: The environment to source when
                                                extracting.
    :return: True if the extraction is successful
    :rtype: boolean
    '''
    if not where.exists():
        where.make()

    if checkout:
        command = "svn checkout --username %(user)s %(remote)s %(where)s" % \
            { 'remote': from_what, 'user' : user, 'where': str(where) }
    else:
        command = ""
        if os.path.exists(str(where)):
            command = "/bin/rm -rf %(where)s && " % \
                { 'remote': from_what, 'where': str(where) }
        
        if tag == "master":
            command += "svn export --username %(user)s %(remote)s %(where)s" % \
                { 'remote': from_what, 'user' : user, 'where': str(where) }       
        else:
            command += "svn export -r %(tag)s --username %(user)s %(remote)s %(where)s" % \
                { 'tag' : tag, 'remote': from_what, 'user' : user, 'where': str(where) }
    
    logger.logTxtFile.write(command + "\n")
    
    logger.write(command + "\n", 5)
    logger.logTxtFile.write("\n" + command + "\n")
    logger.logTxtFile.flush()
    res = SP.call(command, cwd=str(where.dir()),
                           env=environment.environ.environ,
                           shell=True,
                           stdout=logger.logTxtFile,
                           stderr=SP.STDOUT)
    return (res == 0)

DARWIN_PKG_MANAGERS = (
    # (program, default locations, check command)
    ("brew", ("/opt/homebrew/bin/brew", "/usr/local/bin/brew"),
     ["list", "--versions"]),
    ("port", ("/opt/local/bin/port",),
     ["-q", "installed"]),
)

def _get_darwin_pkg_check_cmd():
    '''macOS: command to check if a package is installed, with Homebrew or,
    if it is not installed, MacPorts. Their default locations are also tried:
    /opt/homebrew/bin (Apple Silicon) is often missing from the PATH given to sat.'''
    for prog, locations, args in DARWIN_PKG_MANAGERS:
        exe = prog if shutil.which(prog) else \
              next((l for l in locations if os.access(l, os.X_OK)), None)
        if exe is not None:
            return [exe] + args
    raise src.SatException("Error : command failed because sat was not able to "
                           "find a package manager (brew or port)")

def _check_darwin_pkgs(check_cmd, pkgs, results):
    '''macOS: checks the packages one by one (a name unknown to brew or port
    makes the whole command fail). Fills results {pkg: message}.'''
    env = dict(os.environ)
    env["HOMEBREW_NO_AUTO_UPDATE"] = "1"
    env["HOMEBREW_NO_ENV_HINTS"] = "1"
    is_brew = os.path.basename(check_cmd[0]) == "brew"
    for pkg in pkgs:
        cmds = [check_cmd + [pkg]]
        if is_brew:
            cmds.append(check_cmd + ["--cask", pkg])   # e.g. xquartz
        for cmd in cmds:
            p = SP.Popen(cmd, stdout=SP.PIPE, stderr=SP.DEVNULL, env=env)
            output, _ = p.communicate()
            lines = [l.strip() for l in output.decode("utf-8", "ignore").splitlines()
                     if l.strip()]
            if is_brew:
                # "gcc 15.1.0" (exit code 1 if not installed)
                installed = lines if p.returncode == 0 else []
            else:
                # "  gcc14 @14.2.0_3+stdlib_flag (active)": active versions only
                installed = [l for l in lines if l.endswith("(active)")]
            if installed:
                results[pkg] = src.printcolors.printcSuccess("OK") + \
                               " ({})\n".format(installed[0])
                break

def get_pkg_check_cmd(dist_name):
    '''Build the command to use for checking if a linux package is installed or not.
    macOS: Homebrew (brew list --versions) or MacPorts (port -q installed).'''

    if src.architecture.is_darwin():
        return _get_darwin_pkg_check_cmd()

    if dist_name in ["CO","FD","MG","MD","CO","OS"]: # linux using rpm
        linux="RH"  
        manager_msg_err="Error : command failed because sat was not able to find apt command"
    elif dist_name == "macOS":
        linux="MAC"
        manager_msg_err="Error : command failed because sat was not able to find brew command"
    else:
        linux="DB"
        manager_msg_err="Error : command failed because sat was not able to find rpm command"

    # 1- search for an installed package manager (rpm on rh, apt or dpkg-query on db)
    cmd_which_rpm  = ["which", "rpm"]
    cmd_which_apt  = ["which", "apt"]
    cmd_which_dpkg = ["which", "dpkg-query"]
    cmd_which_brew = ["which", "brew"]
    with open(os.devnull, 'w') as devnull:
        # 1) we search for apt (debian based systems)
        completed=SP.call(cmd_which_dpkg,stdout=devnull, stderr=SP.STDOUT)
        if completed==0 and linux=="DB":
            cmd_is_package_installed = ["dpkg-query", "-l"]
        else:
            # 2) if dpkg not found search for apt
            completed = SP.call(cmd_which_apt, stdout=devnull, stderr=SP.STDOUT)
            if completed == 0 and linux == "DB":
                cmd_is_package_installed = ["apt", "list", "--installed"]
            else:
                # 3) if apt not found search for rpm (redhat)
                completed=SP.call(cmd_which_rpm,stdout=devnull, stderr=SP.STDOUT) # only 3.8! ,capture_output=True)
                if completed==0 and linux=="RH":
                    cmd_is_package_installed=["rpm", "-q"]
                else:
                    # 4) if rpm not found search for brew
                    completed = SP.call(cmd_which_brew, stdout=devnull, stderr=SP.STDOUT)

                    if completed==0 and linux=="MAC":
                        cmd_is_package_installed=["brew", "list"]
                    else:
                        # no package manager was found corresponding to dist_name
                        raise src.SatException(manager_msg_err)
    return cmd_is_package_installed

def check_system_pkgs(check_cmd, pkgs):
    '''Check if a list of packages are installed
    :param check_cmd list: the list of command to use system package manager
    :param pkgs list: the list of pkg names to check
    :rtype: dict
    :return: a dictionary with package name as key and status message as value
    '''
    if not pkgs:
        return {}

    results = {pkg: src.printcolors.printcError("KO") + " (package is not installed!)\n" for pkg in pkgs}
    FNULL = open(os.devnull, 'w')
    cmd = list(check_cmd)

    if check_cmd[0] == "apt":
        cmd.extend([p + "*" for p in pkgs])
        p = SP.Popen(cmd, stdout=SP.PIPE, stderr=FNULL)
        output, _ = p.communicate()
        output = output.decode("utf-8", "ignore")
        
        installed_pkgs_names = set()
        for line in output.splitlines():
            if 'installed' in line:
                installed_pkgs_names.add(line.split('/')[0])

        for installed_name in installed_pkgs_names:
            best_match = ''
            for p in pkgs:
                if installed_name.startswith(p):
                    if len(p) > len(best_match):
                        best_match = p
            if best_match and not results[best_match].startswith('OK'):
                results[best_match] = src.printcolors.printcSuccess("OK") + " ({} is installed)\n".format(installed_name)

    elif check_cmd[0] == "dpkg-query":
        cmd.extend([p + "*" for p in pkgs])
        p = SP.Popen(cmd, stdout=SP.PIPE, stderr=FNULL)
        output, _ = p.communicate()
        output = output.decode("utf-8", "ignore")

        installed_packages = []
        for line in output.splitlines():
            if line.startswith('ii') or line.startswith('ri'):
                parts = line.split()
                if len(parts) > 1:
                    name = parts[1].split(':')[0]
                    version = parts[2]
                    installed_packages.append({'name': name, 'version': version})

        for installed in installed_packages:
            best_match = ''
            for p in pkgs:
                if installed['name'].startswith(p):
                    if len(p) > len(best_match):
                        best_match = p
            if best_match and not results[best_match].startswith('OK'):
                results[best_match] = src.printcolors.printcSuccess("OK") + " ({} {} is installed)\n".format(installed['name'], installed['version'])

    elif check_cmd[0] == "rpm":
        cmd.extend(pkgs)
        p = SP.Popen(cmd, stdout=SP.PIPE, stderr=SP.PIPE)
        stdout, _ = p.communicate()
        stdout = stdout.decode("utf-8", "ignore")
        
        stdout_lines = stdout.strip().split('\n')
        
        for installed_name in stdout_lines:
            if not installed_name or 'is not installed' in installed_name:
                continue
            
            best_match = ''
            for p in pkgs:
                if installed_name.startswith(p + '-'):
                    if len(p) > len(best_match):
                        best_match = p
            
            if best_match and not results[best_match].startswith('OK'):
                results[best_match] = src.printcolors.printcSuccess("OK") + " ({})\n".format(installed_name.strip())

    elif os.path.basename(check_cmd[0]) in ("brew", "port"):
        _check_darwin_pkgs(check_cmd, pkgs, results)

    FNULL.close()
    return results

def check_system_pkg(check_cmd,pkg):
    '''Check if a package is installed
    :param check_cmd list: the list of command to use system package manager
    :param user str: the pkg name to check
    :rtype: str
    :return: a string with package name with status un message
    '''
    return check_system_pkgs(check_cmd, [pkg])[pkg]
