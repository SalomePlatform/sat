#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  Copyright (C) 2010-2018  CEA/DEN
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

"""
This file assume DEBUG functionalities use.
Print salomeTools debug messages in sys.stderr.
Show pretty print debug representation from instances of SAT classes 
(pretty print src.pyconf.Config)

| Warning: supposedly show messages in SAT development phase, not production
| 
| Usage:
| >> import debug as DBG
| >> DBG.write("aTitle", aVariable)        # not shown in production 
| >> DBG.write("aTitle", aVariable, True)  # unconditionaly shown (as show=True)
| 
| to set show message as development phase:
| >> DBG.push_debug(True)
| 
| to set no show message as production phase:
| >> DBG.push_debug(False)
| 
| to set show message temporary as development phase, only in a method:
| >> def aMethodToDebug(...):
| >>   DBG.push_debug(True)              #force show as appended status
| >>   etc. method code with some DBG.write()
| >>   DBG.pop_debug()                   #restore previous status (show or not show)
| >>   return
| 
| to set a message for future fix, as temporary problem to not forget:
| DBG.tofix("aTitle", aVariable, True/False) #True/False in production shown, or not
| 
| in command line interface you could redirect stderr to file 'myDebug.log':
| >> sat compile ... 2> myDebug.log   # only stderr
| >> sat compile ... &> myDebug.log   # stdout and stderr
"""

import os
import sys
import traceback
import pprint as PP
import inspect
import src

# Compatibility python 2/3 for unicode
try:
    _test = unicode
except:
    unicode = str

# Compatibility python 2/3 for StringIO
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

_debug = [False] #support push/pop for temporary activate debug outputs

# wambeke is christian at home
_developers = ["christian", "wambeke"]


def isDeveloper():
    """if you are a developer, sometimes you want verbose traces etc."""
    res = src.architecture.get_user()  in _developers
    return res

def indent(text, amount=2, ch=' '):
    """indent multi lines message"""
    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))

def isTypeConfig(var):
    """To know if var is instance from Config/pyconf"""
    typ = str(type(var))
    # print "isTypeConfig" ,type, dir(var)
    if ".pyconf.Config" in typ: return True
    if ".pyconf.Mapping" in typ: return True
    if ".pyconf.Sequence" in typ: return True
    # print "NOT isTypeConfig %s" % typ
    return False
    
def write(title, var="", force=None, fmt="  %s:\n%s\n####\n"):
    """write sys.stderr a message if _debug[-1]==True or optionaly force=True"""
    if _debug[-1] or force:
      callerframerecord = inspect.stack()[1] # get info of the caller
      frame = callerframerecord[0]
      info = inspect.getframeinfo(frame)
      sys.stderr.write("\n#### DEBUG - %s:%s (%s) ####\n" % (info.filename, info.lineno, info.function))
      tvar = type(var)
      typ = str(tvar)
      if isTypeConfig(var):
        sys.stderr.write(fmt % (title, indent(getStrConfigDbg(var))))
        return
      if 'UnittestStream' in typ:
        sys.stderr.write(fmt % (title, indent(var.getLogs())))
        return  
      if tvar is not str and tvar is not unicode:
        sys.stderr.write(fmt % (title, indent(PP.pformat(var))))
        return
      sys.stderr.write(fmt % (title, indent(var)))
      return
    return

def tofix(title, var="", force=None):
    """
    write sys.stderr a message if _debug[-1]==True or optionaly force=True
    use this only if no logger accessible for classic logger.warning(message)
    """
    if _debug[-1] or isDeveloper():
        callerframerecord = inspect.stack()[1] # get info of the caller
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        fmt = "#### TOFIX - " + str(info.filename) + ":" + str(info.lineno) +\
              " (" + str(info.function) + ") ####\n   %s:\n%s\n"
        write(title, var, force, fmt)

def push_debug(aBool):
    """set debug outputs activated, or not"""
    _debug.append(aBool)

def pop_debug():
    """restore previous debug outputs status"""
    if len(_debug) > 1:
        return _debug.pop()
    else:
        sys.stderr.write("\nERROR: pop_debug: too much pop.")
        return None


def format_exception(msg, limit=None, trace=None):
  """
  Format a stack trace and the exception information.
  as traceback.format_exception(), without color
  with traceback only if (_debug) or (DBG._user in DBG._developers)
  """
  etype, value, tb = sys.exc_info()
  res = msg
  if tb:
    res += "\nTraceback (most recent call last):\n"
    res += "".join(traceback.format_tb(tb, limit))  # [:-1])
  res += "\n"
  res += "\n".join(traceback.format_exception_only(etype, value))
  return res

def format_color_exception(msg, limit=None, trace=None):
  """
  Format a stack trace and the exception information.
  as traceback.format_exception(), with color
  with traceback only if _debug or isDeveloper())
  """
  etype, value, tb = sys.exc_info()
  if _debug[-1] or isDeveloper():
    res = "<red>" + msg
    if tb:
      res += "<yellow>\nTraceback (most recent call last):\n"
      res += "".join(traceback.format_tb(tb, limit))  # [:-1])
    res += "\n<red>"
    res += "\n".join(traceback.format_exception_only(etype, value))
    return res + "<reset>"
  else:
    res = "<red>" + msg  # + "<bright>"
    res += "".join(traceback.format_exception_only(etype, value))
    return res + "<reset>"


###############################################
# utilitaires divers pour debug
###############################################

class OutStream(StringIO):
    """
    utility class for pyconf.Config output iostream
    """
    def close(self):
      """
      because Config.__save__ calls close() stream as file
      keep value before lost as self.value
      """
      self.value = self.getvalue()
      StringIO.close(self)
    
class InStream(StringIO):
    """utility class for pyconf.Config input iostream"""
    pass

def getLocalEnv():
    """get string for environment variables representation"""
    res = ""
    for i in sorted(os.environ):
        res += "%s : %s\n" % (i, os.environ[i])
    return res

# save as initial Config.save() moved as Config.__save__() 
def saveConfigStd(config, aStream):
    """returns as file .pyconf"""
    indent =  0
    config.__save__(aStream, indent) 

def getStrConfigStd(config):
    """set string as saveConfigStd, as file .pyconf"""
    outStream = OutStream()
    saveConfigStd(config, outStream)
    return outStream.value

def getStrConfigDbg(config):
    """
    set string as saveConfigDbg, 
    as (path expression evaluation) for debug
    """
    outStream = OutStream()
    saveConfigDbg(config, outStream)
    return outStream.value

def saveConfigDbg(config, aStream, indent=0, path=""):
    """pyconf returns multilines (path expression evaluation) for debug"""
    _saveConfigRecursiveDbg(config, aStream, indent, path, 0)
    aStream.close() # as config.__save__()

def _saveConfigRecursiveDbg(config, aStream, indent, path, nb):
    """pyconf inspired from Mapping.__save__"""
    debug = False
    nbp = nb + 1 # depth recursive
    if indent <= 0: 
      indentp = 0
    else:
      indentp = indent + 2
      
    if nbp > 10: # protection
      # raise Exception("!!! ERROR: Circular reference after %s" % aStream.getvalue())
      # raise Exception("!!! ERROR: Circular reference %s" % path)
      aStream.write("<red>!!! ERROR: Circular reference after %s<reset>\n" % path)
      return
    
    indstr = indent * ' ' # '':no indent, ' ':indent
    strType = str(type(config))
    if debug: print("saveDbg Type %s %s" % (path, strType))
    
    if "Sequence" in strType:
      for i in range(len(config)):
        _saveConfigRecursiveDbg(config[i], aStream, indentp, path+"[%i]" % i, nbp)
      return
    '''
    if "Reference" in strType:
      try:
        #evaluate = value.resolve(config)
        aStream.write("<header>%s%s<reset> : %s <yellow>--> '%s'<reset>\n" % (indstr, path, config, str(config)))
      except Exception as e:  
        aStream.write("<header>%s%s<reset> : <red>!!! ERROR: %s !!!<reset>\n" % (indstr, path, str(e)))     
      return
    '''
    
    try: #type config, mapping
      order = object.__getattribute__(config, 'order')
      data = object.__getattribute__(config, 'data')
    except:
      aStream.write("%s%s : '%s'\n" % (indstr, path, str(config)))
      return     
    for key in sorted(data): #order): # data as sort alphabetical, order as initial order
      value = data[key]
      strType = str(type(value))
      if debug: print('strType %s %s %s' % (path, key, strType))
      if "Config" in strType:
        _saveConfigRecursiveDbg(value, aStream, indentp, path+"."+key, nbp)
        continue
      if "Mapping" in strType:
        _saveConfigRecursiveDbg(value, aStream, indentp, path+"."+key, nbp)
        continue
      if "Sequence" in strType:
        for i in range(len(value)):
          _saveConfigRecursiveDbg(value.data[i], aStream, indentp, path+"."+key+"[%i]" % i, nbp)
        continue
      if "Expression" in strType:
        try:
          evaluate = value.evaluate(config)
          aStream.write("%s%s.%s : %s --> '%s'\n" % (indstr, path, key, str(value), evaluate))
        except Exception as e:      
          aStream.write("%s%s.%s : !!! ERROR: %s !!!\n" % (indstr, path, key, str(e)))     
        continue
      if "Reference" in strType:
        try:
          evaluate = value.resolve(config)
          aStream.write("%s%s.%s : %s --> '%s'\n" % (indstr, path, key, str(value), evaluate))
        except Exception as e:  
          aStream.write("%s%s.%s : !!! ERROR: %s !!!\n" % (indstr, path, key, str(e)))     
        continue
      if type(value) in [str, bool, int, type(None), unicode]:
        aStream.write("%s%s.%s : '%s'\n" % (indstr, path, key, str(value)))
        continue
      try:
        aStream.write("!!! TODO fix that %s %s%s.%s : %s\n" % (type(value), indstr, path, key, str(value)))
      except Exception as e:      
        aStream.write("%s%s.%s : !!! %s\n" % (indstr, path, key, str(e)))
