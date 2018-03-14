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
This file assume DEBUG functionalities use
- print debug messages in sys.stderr for salomeTools
- show pretty print debug representation from instances of SAT classes
  (pretty print src.pyconf.Config)

WARNING: supposedly show messages in SAT development phase, not production

usage:
>> import debug as DBG
>> DBG.write("aTitle", aVariable)        # not shown in production 
>> DBG.write("aTitle", aVariable, True)  # unconditionaly shown 
"""

import os
import sys
import StringIO as SIO
import pprint as PP

_debug = [False] #support push/pop for temporary activate debug outputs

def indent(text, amount=2, ch=' '):
    """indent multi lines message"""
    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))

def write(title, var="", force=None, fmt="\n#### DEBUG: %s:\n%s\n"):
    """write sys.stderr a message if _debug[-1]==True or optionaly force=True"""
    if _debug[-1] or force:
        if 'src.pyconf.Config' in str(type(var)): 
            sys.stderr.write(fmt % (title, indent(getStrConfigDbg(var))))
        elif type(var) is not str:
            sys.stderr.write(fmt % (title, indent(PP.pformat(var))))
        else:
            sys.stderr.write(fmt % (title, indent(var)))
    return

def tofix(title, var="", force=None):
    """
    write sys.stderr a message if _debug[-1]==True or optionaly force=True
    use this only if no logger accessible for classic logger.warning(message)
    """
    fmt = "\n#### TOFIX: %s:\n%s\n"
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

###############################################
# utilitaires divers pour debug
###############################################

class OutStream(SIO.StringIO):
    """utility class for pyconf.Config output iostream"""
    def close(self):
      """because Config.__save__ calls close() stream as file
      keep value before lost as self.value
      """
      self.value = self.getvalue()
      SIO.StringIO.close(self)
    
class InStream(SIO.StringIO):
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
    """set string as saveConfigStd, 
    as file .pyconf"""
    outStream = OutStream()
    saveConfigStd(config, outStream)
    return outStream.value

def getStrConfigDbg(config):
    """set string as saveConfigDbg, 
    as (path expression evaluation) for debug"""
    outStream = OutStream()
    saveConfigDbg(config, outStream)
    return outStream.value

def saveConfigDbg(config, aStream, indent=0, path=""):
    """pyconf returns multilines (path expression evaluation) for debug"""
    _saveConfigRecursiveDbg(config, aStream, indent, path)
    aStream.close() # as config.__save__()

def _saveConfigRecursiveDbg(config, aStream, indent, path):
    """pyconf inspired from Mapping.__save__"""
    debug = False
    if indent <= 0: 
      indentp = 0
    else:
      indentp = indentp + 2
    indstr = indent * ' ' # '':no indent, ' ':indent
    strType = str(type(config))
    if "Sequence" in strType:
      for i in range(len(config)):
        _saveConfigRecursiveDbg(config[i], aStream, indentp, path+"[%i]" % i)
      return
    try: 
      order = object.__getattribute__(config, 'order')
      data = object.__getattribute__(config, 'data')
    except:
      aStream.write("%s%s : '%s'\n" % (indstr, path, str(config)))
      return     
    for key in sorted(order):
      value = data[key]
      strType = str(type(value))
      if debug: print indstr + 'strType = %s' % strType, key
      if "Config" in strType:
        _saveConfigRecursiveDbg(value, aStream, indentp, path+"."+key)
        continue
      if "Mapping" in strType:
        _saveConfigRecursiveDbg(value, aStream, indentp, path+"."+key)
        continue
      if "Sequence" in strType:
        for i in range(len(value)):
          _saveConfigRecursiveDbg(value[i], aStream, indentp, path+"."+key+"[%i]" % i)
        continue
      if "Expression" in strType:
        try:
          evaluate = value.evaluate(config)
          aStream.write("%s%s.%s : %s --> '%s'\n" % (indstr, path, key, str(value), evaluate))
        except Exception as e:      
          aStream.write("%s%s.%s : !!! ERROR: %s !!!\n" % (indstr, path, key, e.message))     
        continue
      if "Reference" in strType:
        try:
          evaluate = value.resolve(config)
          aStream.write("%s%s.%s : %s --> '%s'\n" % (indstr, path, key, str(value), evaluate))
        except Exception as e:  
          aStream.write("%s%s.%s : !!! ERROR: %s !!!\n" % (indstr, path, key, e.message))     
        continue
      if type(value) in [str, bool, int, type(None), unicode]:
        aStream.write("%s%s.%s : '%s'\n" % (indstr, path, key, str(value)))
        continue
      try:
        aStream.write("!!! TODO fix that %s %s%s.%s : %s\n" % (type(value), indstr, path, key, str(value)))
      except Exception as e:      
        aStream.write("%s%s.%s : !!! %s\n" % (indstr, path, key, e.message))
