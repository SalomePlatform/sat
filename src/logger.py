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

"""\
Implements the classes and method relative to the logging
"""

import sys
import os
import stat
import datetime
import re
import tempfile
import shutil

import src
import printcolors
import xmlManager

import src.debug as DBG

log_macro_command_file_expression = "^[0-9]{8}_+[0-9]{6}_+.*\.xml$"
log_all_command_file_expression = "^.*[0-9]{8}_+[0-9]{6}_+.*\.xml$"

verbose = True # cvw TODO

class Logger(object):
    """\
    Class to handle log mechanism.
    """
    def __init__(self,
                 config= None,
                 silent_sysstd=False,
                 all_in_terminal=False,
                 micro_command = False):
        """Initialization
        
        :param config pyconf.Config: The global configuration.
        :param silent_sysstd boolean: if True, do not write anything
                                      in terminal.
        """
        DBG.write("src.logger.Logger", id(self))
        self.config = config
        self.default_level = 3
        self.silentSysStd = silent_sysstd
        
        # Construct xml log file location for sat prints.
        prefix = ""
        if micro_command:
            prefix = "micro_"
        hour_command_host = (config.VARS.datehour + "_" + 
                             config.VARS.command + "_" + 
                             config.VARS.hostname)
        logFileName = prefix + hour_command_host + ".xml"
        log_dir = src.get_log_path(config)
        logFilePath = os.path.join(log_dir, logFileName)
        # Construct txt file location in order to log 
        # the external commands calls (cmake, make, git clone, etc...)
        txtFileName = prefix + hour_command_host + ".txt"
        txtFilePath = os.path.join(log_dir, "OUT", txtFileName)

        aDirLog = os.path.dirname(logFilePath)
        if not os.path.exists(aDirLog):
          print("create log dir %s" % aDirLog)
          src.ensure_path_exists(aDirLog)
          # sometimes other users make 'sat log' and create hat.xml file...
          os.chmod(aDirLog,
                   stat.S_IRUSR |
                   stat.S_IRGRP |
                   stat.S_IROTH |
                   stat.S_IWUSR |
                   stat.S_IWGRP |
                   stat.S_IWOTH |
                   stat.S_IXUSR |
                   stat.S_IXGRP |
                   stat.S_IXOTH)
        src.ensure_path_exists(os.path.dirname(txtFilePath))
        
        # The path of the log files (one for sat traces, and the other for 
        # the system commands traces)
        self.logFileName = logFileName
        self.logFilePath = logFilePath
        self.txtFileName = txtFileName
        self.txtFilePath = txtFilePath
        
        # The list of all log files corresponding to the current command and
        # the commands called by the current command
        self.l_logFiles = [logFilePath, txtFilePath]
        
        # Initialize xml instance and put first fields 
        # like beginTime, user, command, etc... 
        self.xmlFile = xmlManager.XmlLogFile(logFilePath, "SATcommand", 
                            attrib = {"application" : config.VARS.application})
        self.put_initial_xml_fields()
        # Initialize the txt file for reading
        try:
            self.logTxtFile = open(str(self.txtFilePath), 'w')
        except IOError:
            #msg1 = _("WARNING! Trying to write to a file that"
            #         " is not accessible:")
            #msg2 = _("The logs won't be written.")
            #print("%s\n%s\n%s\n" % (src.printcolors.printcWarning(msg1),
            #                        src.printcolors.printcLabel(str(self.txtFilePath)),
            #                        src.printcolors.printcWarning(msg2) ))
            self.logTxtFile = tempfile.TemporaryFile()
            
        # If the option all_in_terminal was called, all the system commands
        # are redirected to the terminal
        if all_in_terminal:
            self.logTxtFile = sys.__stdout__
        
    def put_initial_xml_fields(self):
        """\
        Called at class initialization: Put all fields 
        corresponding to the command context (user, time, ...)
        """
        # command name
        self.xmlFile.add_simple_node("Site", attrib={"command" : 
                                                     self.config.VARS.command})
        # version of salomeTools
        self.xmlFile.append_node_attrib("Site", attrib={"satversion" : 
                                            src.get_salometool_version(self.config)})
        # machine name on which the command has been launched
        self.xmlFile.append_node_attrib("Site", attrib={"hostname" : 
                                                    self.config.VARS.hostname})
        # Distribution of the machine
        self.xmlFile.append_node_attrib("Site", attrib={"OS" : 
                                                        self.config.VARS.dist})
        # The user that have launched the command
        self.xmlFile.append_node_attrib("Site", attrib={"user" : 
                                                        self.config.VARS.user})
        # The time when command was launched
        Y, m, dd, H, M, S = date_to_datetime(self.config.VARS.datehour)
        date_hour = "%4s/%2s/%2s %2sh%2sm%2ss" % (Y, m, dd, H, M, S)
        self.xmlFile.append_node_attrib("Site", attrib={"beginTime" : 
                                                        date_hour})
        # The application if any
        if "APPLICATION" in self.config:
            self.xmlFile.append_node_attrib("Site", 
                        attrib={"application" : self.config.VARS.application})
        # The initialization of the trace node
        self.xmlFile.add_simple_node("Log",text="")
        # The system commands logs
        self.xmlFile.add_simple_node("OutLog",
                                    text=os.path.join("OUT", self.txtFileName))
        # The initialization of the node where 
        # to put the links to the other sat commands that can be called by any
        # command 
        self.xmlFile.add_simple_node("Links")

    def add_link(self,
                 log_file_name,
                 command_name,
                 command_res,
                 full_launched_command):
        """Add a link to another log file.
        
        :param log_file_name str: The file name of the link.
        :param command_name str: The name of the command linked.
        :param command_res str: The result of the command linked. "0" or "1"
        :parma full_launched_command str: The full lanch command 
                                          ("sat command ...")
        """
        xmlLinks = self.xmlFile.xmlroot.find("Links")
        flc = src.xmlManager.escapeSequence(full_launched_command)
        att = {"command" : command_name, "passed" : str(command_res), "launchedCommand" : flc}
        src.xmlManager.add_simple_node(xmlLinks, "link", text = log_file_name, attrib = att)

    def write(self, message, level=None, screenOnly=False):
        """\
        function used in the commands 
        to print in the terminal and the log file.
        
        :param message str: The message to print.
        :param level int: The output level corresponding 
                          to the message 0 < level < 6.
        :param screenOnly boolean: if True, do not write in log file.
        """
        # avoid traces if unittest
        if isCurrentLoggerUnittest():
            # print("doing unittest")
            sendMessageToCurrentLogger(message, level)
            return

        # do not write message starting with \r to log file
        if not message.startswith("\r") and not screenOnly:
            self.xmlFile.append_node_text("Log", 
                                          printcolors.cleancolor(message))

        # get user or option output level
        current_output_verbose_level = self.config.USER.output_verbose_level
        if not ('isatty' in dir(sys.stdout) and sys.stdout.isatty()):
            # clean the message color if the terminal is redirected by user
            # ex: sat compile appli > log.txt
            message = printcolors.cleancolor(message)
        
        # Print message regarding the output level value
        if level:
            if level <= current_output_verbose_level and not self.silentSysStd:
                sys.stdout.write(message)
        else:
            if self.default_level <= current_output_verbose_level and not self.silentSysStd:
                sys.stdout.write(message)
        self.flush()

    def error(self, message, prefix="ERROR: "):
      """Print an error.

      :param message str: The message to print.
      """
      # Print in the log file
      self.xmlFile.append_node_text("traces", prefix + message)

      # Print in the terminal and clean colors if the terminal
      # is redirected by user
      if not ('isatty' in dir(sys.stderr) and sys.stderr.isatty()):
        sys.stderr.write(printcolors.printcError(prefix + message + "\n"))
      else:
        sys.stderr.write(prefix + message + "\n")

    def step(self, message):
      """Print an step message.

      :param message str: The message to print.
      """
      self.write('STEP: ' + message, level=4)

    def trace(self, message):
      """Print an trace message.

      :param message str: The message to print.
      """
      self.write('TRACE: ' + message, level=5)

    def debug(self, message):
      """Print an debug message.

      :param message str: The message to print.
      """
      self.write('DEBUG: ' + message, level=6)

    def warning(self, message):
      """Print an warning message.

      :param message str: The message to print.
      """
      self.error(message, prefix="WARNING: ")

    def critical(self, message):
      """Print an critical message.

      :param message str: The message to print.
      """
      self.error(message, prefix="CRITICAL: ")



    def flush(self):
        """Flush terminal"""
        sys.stdout.flush()
        self.logTxtFile.flush()
        
    def end_write(self, attribute):
        """\
        Called just after command end: Put all fields 
        corresponding to the command end context (time).
        Write the log xml file on the hard drive.
        And display the command to launch to get the log
        
        :param attribute dict: the attribute to add to the node "Site".
        """       
        # Get current time (end of command) and format it
        dt = datetime.datetime.now()
        Y, m, dd, H, M, S = date_to_datetime(self.config.VARS.datehour)
        t0 = datetime.datetime(int(Y), int(m), int(dd), int(H), int(M), int(S))
        tf = dt
        delta = tf - t0
        total_time = timedelta_total_seconds(delta)
        hours = int(total_time / 3600)
        minutes = int((total_time - hours*3600) / 60)
        seconds = total_time - hours*3600 - minutes*60
        # Add the fields corresponding to the end time
        # and the total time of command
        endtime = dt.strftime('%Y/%m/%d %Hh%Mm%Ss')
        self.xmlFile.append_node_attrib("Site", attrib={"endTime" : endtime})
        self.xmlFile.append_node_attrib("Site", 
                attrib={"TotalTime" : "%ih%im%is" % (hours, minutes, seconds)})
        
        # Add the attribute passed to the method
        self.xmlFile.append_node_attrib("Site", attrib=attribute)
        
        # Call the method to write the xml file on the hard drive
        self.xmlFile.write_tree(stylesheet = "command.xsl")

        # so unconditionnaly copy stylesheet file(s)
        xslDir = os.path.join(self.config.VARS.srcDir, 'xsl')
        xslCommand = "command.xsl"
        # xslHat = "hat.xsl" # have to be completed (one time at end)
        xsltest = "test.xsl"
        imgLogo = "LOGO-SAT.png"
        files_to_copy = [xslCommand, xsltest, imgLogo]

        logDir = src.get_log_path(self.config)
        # copy the stylesheets in the log directory as soon as possible here
        # because referenced in self.xmlFile.write_tree above
        # OP We use copy instead of copy2 to update the creation date
        #    So we can clean the LOGS directories easily
        for f in files_to_copy:
          f_init = os.path.join(xslDir, f)
          f_target = os.path.join(logDir, f)
          if not os.path.isfile(f_target): # do not overrride
            shutil.copy(f_init, logDir)
        
        # Dump the config in a pyconf file in the log directory
        dumpedPyconfFileName = (self.config.VARS.datehour
                                + "_" 
                                + self.config.VARS.command 
                                + ".pyconf")
        dumpedPyconfFilePath = os.path.join(logDir, 'OUT', dumpedPyconfFileName)
        try:
            f = open(dumpedPyconfFilePath, 'w')
            self.config.__save__(f)
            f.close()
        except IOError:
            pass

def date_to_datetime(date):
    """\
    From a string date in format YYYYMMDD_HHMMSS
    returns list year, mon, day, hour, minutes, seconds 
    
    :param date str: The date in format YYYYMMDD_HHMMSS
    :return: the same date and time in separate variables.
    :rtype: (str,str,str,str,str,str)
    """
    Y = date[:4]
    m = date[4:6]
    dd = date[6:8]
    H = date[9:11]
    M = date[11:13]
    S = date[13:15]
    return Y, m, dd, H, M, S

def timedelta_total_seconds(timedelta):
    """\
    Replace total_seconds from datetime module 
    in order to be compatible with old python versions
    
    :param timedelta datetime.timedelta: The delta between two dates
    :return: The number of seconds corresponding to timedelta.
    :rtype: float
    """
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6
        
def show_command_log(logFilePath, cmd, application, notShownCommands):
    """\
    Used in updateHatXml. 
    Determine if the log xml file logFilePath 
    has to be shown or not in the hat log.
    
    :param logFilePath str: the path to the command xml log file
    :param cmd str: the command of the log file
    :param application str: the application passed as parameter 
                            to the salomeTools command
    :param notShownCommands list: the list of commands 
                                  that are not shown by default
    
    :return: True if cmd is not in notShownCommands and the application 
             in the log file corresponds to application
    :rtype: boolean
    """
    # When the command is not in notShownCommands, no need to go further :
    # Do not show
    if cmd in notShownCommands:
        return False, None, None
 
    # Get the application of the log file
    try:
        logFileXml = src.xmlManager.ReadXmlFile(logFilePath)
    except Exception as e:
        msg = _("WARNING: the log file %s cannot be read:" % logFilePath)
        sys.stdout.write(printcolors.printcWarning("%s\n%s\n" % (msg, e)))
        return False, None, None

    try:
        if 'application' in logFileXml.xmlroot.keys():
          appliLog = logFileXml.xmlroot.get('application')
          launched_cmd = logFileXml.xmlroot.find('Site').attrib['launchedCommand']
          # if it corresponds, then the log has to be shown
          if appliLog == application:
              return True, appliLog, launched_cmd
          elif application != 'None':
              return False, appliLog, launched_cmd

          return True, appliLog, launched_cmd
    except Exception as e:
        msg = _("WARNING: the log file %s cannot be parsed:" % logFilePath)
        sys.stdout.write(printcolors.printcWarning("%s\n%s\n" % (msg, e)))
        return False, None, None

    if application == 'None':
            return True, None, None
        
    return False, None, None

def list_log_file(dirPath, expression):
    """Find all files corresponding to expression in dirPath
    
    :param dirPath str: the directory where to search the files
    :param expression str: the regular expression of files to find
    :return: the list of files path and informations about it
    :rtype: list
    """
    lRes = []
    for fileName in os.listdir(dirPath):
        # YYYYMMDD_HHMMSS_namecmd.xml
        sExpr = expression
        oExpr = re.compile(sExpr)
        if oExpr.search(fileName):
            file_name = fileName
            if fileName.startswith("micro_"):
                file_name = fileName[len("micro_"):]
            # get date and hour and format it
            date_hour_cmd_host = file_name.split('_')
            date_not_formated = date_hour_cmd_host[0]
            date = "%s/%s/%s" % (date_not_formated[6:8], 
                                 date_not_formated[4:6], 
                                 date_not_formated[0:4])
            hour_not_formated = date_hour_cmd_host[1]
            hour = "%s:%s:%s" % (hour_not_formated[0:2], 
                                 hour_not_formated[2:4], 
                                 hour_not_formated[4:6])
            if len(date_hour_cmd_host) < 4:
                cmd = date_hour_cmd_host[2][:-len('.xml')]
                host = ""
            else:
                cmd = date_hour_cmd_host[2]
                host = date_hour_cmd_host[3][:-len('.xml')]
            lRes.append((os.path.join(dirPath, fileName), 
                         date_not_formated,
                         date,
                         hour_not_formated,
                         hour,
                         cmd,
                         host))
    return lRes

def update_hat_xml(logDir, application=None, notShownCommands = []):
    """\
    Create the xml file in logDir that contain all the xml file 
    and have a name like YYYYMMDD_HHMMSS_namecmd.xml
    
    :param logDir str: the directory to parse
    :param application str: the name of the application if there is any
    """
    # Create an instance of XmlLogFile class to create hat.xml file
    xmlHatFilePath = os.path.join(logDir, 'hat.xml')
    xmlHat = src.xmlManager.XmlLogFile(xmlHatFilePath, "LOGlist", {"application" : application})
    # parse the log directory to find all the command logs, 
    # then add it to the xml file
    lLogFile = list_log_file(logDir, log_macro_command_file_expression)
    for filePath, __, date, __, hour, cmd, __ in lLogFile:
        showLog, cmdAppli, full_cmd = show_command_log(filePath, cmd,
                                              application, notShownCommands)
        #if cmd not in notShownCommands:
        if showLog:
            # add a node to the hat.xml file
            xmlHat.add_simple_node("LogCommand", 
                                   text=os.path.basename(filePath), 
                                   attrib = {"date" : date, 
                                             "hour" : hour, 
                                             "cmd" : cmd, 
                                             "application" : cmdAppli,
                                             "full_command" : full_cmd})
    
    # Write the file on the hard drive
    xmlHat.write_tree('hat.xsl')
    # Sometimes other users will make 'sat log' and update this file
    os.chmod(xmlHatFilePath,
             stat.S_IRUSR |
             stat.S_IRGRP |
             stat.S_IROTH |
             stat.S_IWUSR |
             stat.S_IWGRP |
             stat.S_IWOTH )



# TODO for future
# prepare skip to logging logger sat5.1
# suppose only one logger in sat5.1
_currentLogger = []

def getCurrentLogger():
  """get current logging logger, set as DefaultLogger if not set yet"""
  if len(_currentLogger) == 0:
    import src.loggingSimple as LOGSI
    logger = LOGSI.getDefaultLogger()
    _currentLogger.append(logger)
    logger.warning("set by default current logger as %s" % logger.name)
  return _currentLogger[0]

def getDefaultLogger():
  """get simple logging logger DefaultLogger, set it as current"""
  import src.loggingSimple as LOGSI
  logger = LOGSI.getDefaultLogger()
  setCurrentLogger(logger) # set it as current
  return logger

def getUnittestLogger():
  """get simple logging logger UnittestLogger, set it as current"""
  import src.loggingSimple as LOGSI
  logger = LOGSI.getUnittestLogger()
  setCurrentLogger(logger) # set it as current
  return logger

def setCurrentLogger(logger):
  """temporary send all in stdout as simple logging logger"""
  if len(_currentLogger) == 0:
    _currentLogger.append(logger)
    logger.debug("set current logger as %s" % logger.name)
  else:
    if _currentLogger[0].name != logger.name:
      # logger.debug("quit current logger as default %s" % _currentLogger[0].name)
      _currentLogger[0] = logger
      logger.warning("change current logger as %s" % logger.name)
  return _currentLogger[0]

def isCurrentLoggerUnittest():
    logger = getCurrentLogger()
    if "Unittest" in logger.name:
      res = True
    else:
      res = False
    #DBG.write("isCurrentLoggerUnittest %s" % logger.name, res)
    return res

def sendMessageToCurrentLogger(message, level):
    """
    assume relay from obsolescent
    logger.write(msg, 1/2/3...) to future
    logging.critical/warning/info...(msg) (as logging package tips)
    """
    logger = getCurrentLogger()
    if level is None:
      lev = 2
    else:
      lev = level
    if lev <= 1:
      logger.critical(message)
      return
    if lev == 2:
      logger.warning(message)
      return
    if lev == 3:
      logger.info(message)
      return
    if lev == 4:
      logger.step(message)
      return
    if lev == 5:
      logger.trace(message)
      return
    if lev >= 6:
      logger.debug(message)
      return
    msg = "What is this level: '%s' for message:\n%s" % (level, message)
    logger.warning(msg)
    return
