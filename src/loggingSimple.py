#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
salomeTools logger. using logging package

| http://sametmax.com/ecrire-des-logs-en-python/
|
| Define two LoggerSat instances in salomeTools, no more need.
|   - _loggerDefault as production/development logger
|   - _loggerUnittest as unittest logger
|

"""


import os
import sys
import time
import random
import logging as LOGI

from logging.handlers import BufferingHandler
import pprint as PP

import src.debug as DBG  # Easy print stderr (for DEBUG only)

_verbose = False
_name = "loggingSimple"
_loggerDefaultName = 'SimpleDefaultLogger'
_loggerUnittestName = 'SimpleUnittestLogger'

_STEP = LOGI.INFO - 1  # step level is just below INFO
_TRACE = LOGI.INFO - 2  # trace level is just below STEP

LOGI.STEP = _STEP  # only for coherency,
LOGI.TRACE = _TRACE  # only for coherency,

_knownLevels = "CRITICAL ERROR WARNING INFO STEP TRACE DEBUG".upper().split()
_knownLevelsStr = "[%s]" % "|".join(_knownLevels)


#################################################################
# utilities methods
#################################################################

def filterLevel(aLevel):
  """
  filter levels logging values from firsts characters levels.
  No case sensitive

  | example:
  | 'i' -> 'INFO'
  | 'cRiT' -> 'CRITICAL'
  """
  aLev = aLevel.upper()
  knownLevels = _knownLevels
  maxLen = max([len(i) for i in knownLevels])
  for i in range(maxLen):
    for lev in knownLevels:
      if aLev == lev[:i]:
        # DBG.write("filterLevel", "%s -> %s" % (aLevel, lev))
        return lev
  msg = "Unknown level '%s', accepted are:\n%s" % (aLev, ", ".join(knownLevels))
  return msg
  # raise Exception(msg)


def indent(msg, nb, car=" "):
  """indent nb car (spaces) multi lines message except first one"""
  s = msg.split("\n")
  res = ("\n" + car * nb).join(s)
  return res


def indentUnittest(msg, prefix=" | "):
  """
  indent multi lines message except first one with prefix.
  prefix default is designed for less spaces for size logs files
  and keep logs human eye readable
  """
  s = msg.split("\n")
  res = ("\n" + prefix).join(s)
  return res


def log(msg, force=False):
  """elementary log when no logging.Logger yet"""
  prefix = "---- %s.log: " % _name
  nb = len(prefix)
  if _verbose or force:
    print(prefix + indent(msg, nb))


# just for debug info where is import logging
log("import logging on %s" % LOGI.__file__)


def getStrDirLogger(logger):
  """
  Returns multi line string for logger description, with dir(logger).
  Used for debug
  """
  lgr = logger  # shortcut
  msg = "%s(name=%s, dateLogger=%s):\n%s\n"
  cName = lgr.__class__.__name__
  res = msg % (cName, lgr.name, lgr.dateLogger, PP.pformat(dir(lgr)))
  return res


def getStrHandler(handler):
  """
  Returns one line string for handler description
  (as inexisting __repr__)
  to avoid create inherited classe(s) handler
  """
  h = handler  # shortcut
  msg = "%s(name=%s)"
  cName = h.__class__.__name__
  # get_name absent in logging 0.5.0.5 python 2.6
  res = msg % (cName, h._name)
  return res


def getStrShort(msg):
  """Returns short string for msg (as first caracters without line feed"""
  # log("getStrShort " + str(msg), True)
  res = msg.replace("\n", "//")[0:30]
  return res


def getStrLogRecord(logRecord):
  """
  Returns one line string for simple logging LogRecord description
  """
  msg = "LogRecord(level='%s', msg='%s...')"
  shortMsg = getStrShort(logRecord.msg)
  levelName = logRecord.levelname
  res = msg % (levelName, shortMsg)
  return res


def getListOfStrLogRecord(listOfLogRecord):
  """
  Returns one line string for logging LogRecord description
  """
  res = [getStrLogRecord(l) for l in listOfLogRecord]
  return res


#################################################################
# salometools logger classes
#################################################################

try:
  unicode
  _unicode = True
except NameError:
  _unicode = False


def getMessage(self):
  """
  modified from logging.__init__.LogRecord.getMessage,
  better message on format error
  Return the message for this LogRecord.

  Return the message for this LogRecord after merging any user-supplied
  arguments with the message.
  """
  if not _unicode:  # if no unicode support...
    msg = str(self.msg)
  else:
    msg = self.msg
    if not isinstance(msg, basestring):
      try:
        msg = str(self.msg)
      except UnicodeError:
        msg = self.msg  # Defer encoding till later
  if self.args:
    try:  # better message on format error
      msg = msg % self.args
    except Exception as e:
      msg = "ERROR: %s with args %s" % (msg, PP.pformat(self.args))
      log(msg, True)
  return msg


LOGI.LogRecord.getMessage = getMessage  # better message if error


#################################################################
class LoggerSimple(LOGI.Logger, object): # object force new-style classes in logging 0.5.0.5 python 2.6
  """
  Inherited class logging.Logger for logger salomeTools

  | add a level STEP as log.step(msg)
  | add a level TRACE as log.trace(msg)
  | below log.info(msg)
  | above log.debug(msg)
  | to assume message step inside files xml 'command's internal traces'
  | to assume store long log asci in files txt outside files xml
  |
  | see: /usr/lib64/python2.7/logging/__init__.py etc.
  """

  def __init__(self, name, level=LOGI.INFO):
    """
    Initialize the logger with a name and an optional level.
    """
    super(LoggerSimple, self).__init__(name, level)
    LOGI.addLevelName(_STEP, "STEP")
    LOGI.addLevelName(_TRACE, "TRACE")
    self.dateLogger = "NoDateLogger"
    self.dateHour = None  # datehour of main command
    self.isClosed = False
    self.STEP = _STEP
    self.TRACE = _TRACE

  def close(self):
    """
    final stuff for logger, done at end salomeTools
    flushed and closed xml files have to be not overriden/appended
    """
    if self.isClosed:
      raise Exception("logger closed yet: %s" % self)
    log("close stuff logger %s" % self)  # getStrDirLogger(self)
    for handl in list(self.handlers):  # get original list
      log("close stuff handler %s" % getStrHandler(handl))
      handl.close()  # Tidy up any resources used by the handler.
      self.removeHandler(handl)
    # todo etc
    self.isClosed = True  # done at end of execution
    return

  def __repr__(self):
    """one line string representation"""
    msg = "%s(name=%s, dateLogger=%s, handlers=%s)"
    cName = self.__class__.__name__
    h = [getStrHandler(h) for h in self.handlers]
    h = "[" + ", ".join(h) + "]"
    res = msg % (cName, self.name, self.dateLogger, h)
    return res

  def trace(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity '_TRACE'.
    """
    log("trace stuff logger '%s' msg '%s...'" % (self.name, getStrShort(msg)))
    if self.isEnabledFor(_TRACE):
      self._log(_TRACE, msg, args, **kwargs)

  def step(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity '_STEP'.
    """
    log("step stuff logger '%s' msg '%s...'" % (self.name, getStrShort(msg)))
    if self.isEnabledFor(_STEP):
      self._log(_STEP, msg, args, **kwargs)

  def setLevelMainHandler(self, level):
    handl =  self.handlers[0]  # get main handler
    log("setLevelMainHandler %s" % level)
    handl.setLevel(level)


#################################################################
class UnittestFormatter(LOGI.Formatter, object): # object force new-style classes in logging 0.5.0.5 python 2.6
  """
  this formatter prefixes level name and indents all messages
  """
  def format(self, record):
    # print "", record.levelname #type(record), dir(record)
    # nb = len("2018-03-17 12:15:41 :: INFO     :: ")
    res = super(UnittestFormatter, self).format(record)
    res = indentUnittest(res)
    return res

#################################################################
class DefaultFormatter(LOGI.Formatter, object): # object force new-style classes in logging 0.5.0.5 python 2.6
  """
  this formatter prefixes level name and indents all messages but INFO stay "as it"
  """
  def format(self, record):
    # print "", record.levelname #type(record), dir(record)
    # nb = len("2018-03-17 12:15:41 :: INFO     :: ")
    if record.levelname == "INFO":
      res = record.getMessage()
    else:
      res = super(DefaultFormatter, self).format(record)
      res = indentUnittest(res)
    return res


#################################################################
class UnittestStream(object):
  """
  write my stream class
  only write and flush are used for the streaming

  | https://docs.python.org/2/library/logging.handlers.html
  | https://stackoverflow.com/questions/31999627/storing-logger-messages-in-a-string
  """

  def __init__(self):
    self._logs = ''

  def getLogs(self):
    return self._logs

  def getLogsAndClear(self):
    res = self._logs
    self._logs = ''
    return res

  def write(self, astr):
    """final method called when message is logged"""
    # log("UnittestStream.write('%s')" % astr, True) # for debug ...
    self._logs += astr

  def flush(self):
    pass

  def __str__(self):
    return self._logs


#################################################################
class StreamHandlerSimple(LOGI.StreamHandler, object): # object force new-style classes in logging 0.5.0.5 python 2.6
  """
  A handler class which writes logging records, appropriately formatted,
  to a stream. Note that this class does not close the stream, as
  sys.stdout or sys.stderr may be used.

  from logging.StreamHandler class,
  modified for 'no return' mode line if '...' at end of record message
  """

  def emit(self, record):
    """
    Emit a record.

    If a formatter is specified, it is used to format the record.
    The record is then written to the stream with a trailing newline.  If
    exception information is present, it is formatted using
    traceback.print_exception and appended to the stream.  If the stream
    has an 'encoding' attribute, it is used to determine how to do the
    output to the stream.
    """
    # log("StreamHandlerSimple.emit('%s')" % record, True) # for debug ...
    try:
      msg = self.format(record)
      stream = self.stream
      fs = '%s\n'
      ufs = u'%s\n'
      if not _unicode:  # if no unicode support...
        stream.write(fs % msg)
      else:
        try:
          if (isinstance(msg, unicode) and
            getattr(stream, 'encoding', None)):
            # ufs = u'%s\n'
            try:
              stream.write(ufs % msg)
            except UnicodeEncodeError:
              # Printing to terminals sometimes fails. For example,
              # with an encoding of 'cp1251', the above write will
              # work if written to a stream opened or wrapped by
              # the codecs module, but fail when writing to a
              # terminal even when the codepage is set to cp1251.
              # An extra encoding step seems to be needed.
              stream.write((ufs % msg).encode(stream.encoding))
          else:
            stream.write(fs % msg)
        except UnicodeError:
          stream.write(fs % msg.encode("UTF-8"))
      self.flush()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      self.handleError(record)



#################################################################
# methods to define two LoggerSimple instances in salomeTools,
# no more need
#################################################################
def initLoggerAsDefault(logger, fmt=None, level=None):
  """
  init logger as prefixed message and indented message if multi line
  exept info() outed 'as it' without any format.
  level could be modified during execution
  """
  log("initLoggerAsDefault name=%s\nfmt='%s' level='%s'" % (logger.name, fmt, level))
  #handler = StreamHandlerSimple(sys.stdout)  # Logging vers console
  handler = LOGI.StreamHandler(sys.stdout)  # Logging vers console
  # set_name absent in logging 0.5.0.5 python 2.6
  handler._name = logger.name + "_console"
  if fmt is not None:
    # formatter = UnittestFormatter(fmt, "%y-%m-%d %H:%M:%S")
    formatter = DefaultFormatter(fmt, "%y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
  handler.idCommandHandlers = 0
  logger.addHandler(handler)
  # as RootLogger is level WARNING
  # my logger is not notset but low, handlers needs setlevel greater
  logger.setLevel(LOGI.DEBUG)
  # import src/debug as DBG
  # tmp = (logger.getEffectiveLevel(), LOGI.NOTSET, logger.level, logger.parent.level)
  # DBG.write("logger levels tmp, True)
  if level is not None:  # level could be modified during execution
    handler.setLevel(level)  # on screen log as user wants
  else:
    handler.setLevel(LOGI.INFO)  # on screen no log step, which are in xml files
  return


def initLoggerAsUnittest(logger, fmt=None, level=None):
  """
  init logger as silent on stdout/stderr
  used for retrieve messages in memory for post execution unittest
  https://docs.python.org/2/library/logging.handlers.html
  """
  log("initLoggerAsUnittest name=%s\nfmt='%s' level='%s'" % (logger.name, fmt, level))
  stream = UnittestStream()
  handler = LOGI.StreamHandler(stream)  # Logging vers stream
  # set_name absent in logging 0.5.0.5 python 2.6
  handler._name = logger.name + "_unittest"
  if fmt is not None:
    # formatter = LOGI.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
    formatter = UnittestFormatter(fmt, "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
  handler.idCommandHandlers = 0
  logger.addHandler(handler)
  logger.stream = stream
  logger.getLogs = stream.getLogs
  logger.getLogsAndClear = stream.getLogsAndClear
  if level is not None:
    logger.setLevel(level)
  else:
    logger.setLevel(LOGI.DEBUG)


def getDefaultLogger():
  log("getDefaultLogger %s" % _loggerDefaultName)
  # case multithread may be problem as not LOGI._acquireLock()
  previousClass = LOGI._loggerClass
  LOGI.setLoggerClass(LoggerSimple)  # to get LoggerSimple instance with trace etc.
  res = LOGI.getLogger(_loggerDefaultName)
  LOGI.setLoggerClass(previousClass)
  return res


def getUnittestLogger():
  log("getUnittestLogger %s" % _loggerUnittestName)
  # case multithread may be problem as not LOGI._acquireLock()
  previousClass = LOGI._loggerClass
  LOGI.setLoggerClass(LoggerSimple)  # to get LoggerSimple instance with trace etc.
  res = LOGI.getLogger(_loggerUnittestName)
  LOGI.setLoggerClass(previousClass)
  return res


#################################################################
# small tests as demonstration, see unittest also
#################################################################
def testLogger_2(logger):
  """small test"""
  # print getStrDirLogger(logger)
  logger.debug('test logger debug')
  logger.trace('test logger trace')
  logger.info('test logger info')
  logger.warning('test logger warning')
  logger.error('test logger error')
  logger.critical('test logger critical')
  logger.info('\ntest logger info:\n- second line\n- third line\n')
  logger.warning('test logger warning:\n- second line\n- third line')

def testMain_2():
  print("\n**** DEFAULT logger")
  logdef = getDefaultLogger()
  # use of setColorLevelname <color>...<reset>, so do not use %(levelname)-8s
  initLoggerAsDefault(logdef, '%(levelname)-8s :: %(message)s', level=LOGI.DEBUG)
  testLogger_2(logdef)

  print("\n**** UNITTEST logger")
  loguni = getUnittestLogger()
  initLoggerAsUnittest(loguni, '%(asctime)s :: %(levelname)-8s :: %(message)s', level=LOGI.DEBUG)
  testLogger_2(loguni)  # is silent
  # log("loguni.getLogs():\n%s" % loguni.getLogs())
  print("loguni.streamUnittest:\n%s" % loguni.getLogs())


#################################################################
# in production, or not (if __main__)
#################################################################
if __name__ == "__main__":
  # for example, not in production
  # get path to salomeTools sources
  curdir = os.path.dirname(os.path.dirname(__file__))
  # Make the src & commands package accessible from all code
  sys.path.insert(0, curdir)
  testMain_2()
  # here we have sys.exit()
else:
  # in production
  # get two LoggerSat instance used in salomeTools, no more needed.
  _loggerDefault = getDefaultLogger()
  _loggerUnittest = getUnittestLogger()
  initLoggerAsDefault(_loggerDefault, '%(levelname)-8s :: %(message)s')
  initLoggerAsUnittest(_loggerUnittest, '%(asctime)s :: %(levelname)s :: %(message)s')
