#!/usr/bin/env python
#-*- coding:utf-8 -*-

# https://gist.github.com/techtonik/2151727
# Public Domain, i.e. feel free to copy/paste
# Considered a hack in Python 2

import os
import sys
import inspect
import logging
import pprint as PP


##############################################################################
def caller_name_simple(skip=1):
  """
  Get a name of a caller in the format module.class.method

  'skip' specifies how many levels of stack to skip while getting caller
  name. skip=1 means 'who calls me', skip=2 'who calls my caller' etc.

  An empty string is returned if skipped levels exceed stack height
  """

  def stack_(frame):
    framelist = []
    while frame:
      framelist.append(frame)
      frame = frame.f_back
    return framelist

  stack = stack_(sys._getframe(1))
  start = 0 + skip
  if len(stack) < start + 1:
    return ''
  parentframe = stack[start]

  name = []
  module = inspect.getmodule(parentframe)
  # `modname` can be None when frame is executed directly in console
  # TODO(techtonik): consider using __main__
  if module:
    name.append(module.__name__)
  # detect classname
  if 'self' in parentframe.f_locals:
    # I don't know any way to detect call from the object method
    # XXX: there seems to be no way to detect static method call - it will
    #      be just a function call
    name.append(parentframe.f_locals['self'].__class__.__name__)
  codename = parentframe.f_code.co_name

  fr = inspect.currentframe().f_back
  for i in range(skip):  # no more 20 for precaution
    fr = fr.f_back
    if fr is None:
      break
  lineno = fr.f_lineno

  if codename != '<module>':  # top level usually
    name.append(codename)

  name[-1] += "[%s]" % str(lineno)  # function or a method
  del parentframe
  return ".".join(name)


##############################################################################
def caller_name_stack(skip=1):
  """
  Get a name of a caller in the format module[no].class[no].method[no]
  where [no] is line nunber in source file(s)

  'skip' specifies how many levels of stack to skip while getting caller
  name. skip=1 means 'who calls me', skip=2 'who calls my caller' etc.

  An empty string is returned if skipped levels exceed stack height
  """
  def stack_(frame):
    framelist = []
    while frame:
      framelist.append(frame)
      frame = frame.f_back
    return framelist

  stack = stack_(sys._getframe(1))
  start = 0 + skip
  if len(stack) < start + 1:
    return ''
  parentframe = stack[start]

  name = []
  module = inspect.getmodule(parentframe)
  # `modname` can be None when frame is executed directly in console
  # TODO(techtonik): consider using __main__
  if module:
    name.append(module.__name__)
  # detect classname
  if 'self' in parentframe.f_locals:
    # I don't know any way to detect call from the object method
    # XXX: there seems to be no way to detect static method call - it will
    #      be just a function call
    name.append(parentframe.f_locals['self'].__class__.__name__)
  codename = parentframe.f_code.co_name

  fr = inspect.currentframe().f_back
  lineno = [fr.f_lineno]
  for i in range(20):  # no more 20 for precaution
    fr = fr.f_back
    if fr is None:
      break
    #print("*** frame locals %s" % str(fr.f_locals.keys()))
    #print("*** frame globals %s" % str(fr.f_globals.keys()))
    try:
      namesrc = fr.f_globals["__name__"]
      if namesrc == "__main__":
        namesrc = os.path.basename(fr.f_globals["__file__"])
      lineno.insert(0, (namesrc + "[%s]" % fr.f_lineno))
    except:
      lineno.insert(0, ("??", fr.f_lineno))

  if codename != '<module>':  # top level usually
    name.append(codename)  # function or a method

  #print("lineno", lineno)
  #print("name", name)

  name[-1] += " // STACK: %s" % " ".join(lineno[0:-1])

  del parentframe
  return ".".join(name)


##############################################################################
def example_of_use(toCall):
  """
  example of use caller_name_simple, or else
  """
  class Dummy:
    def one_method(self):
      print("4- call in class %s" % toCall(0))

  print("1- call in %s" % toCall(0)) # output from main to here
  print("2- call in %s" % toCall(0))
  print("3- call in %s" % toCall(1)) # output from main to caller
  tmp = Dummy()
  tmp.one_method()


##############################################################################
# main as an example
##############################################################################
if __name__ == "__main__":
  example_of_use(caller_name_simple)
  example_of_use(caller_name_stack)

"""
example of output

1- call in __main__.example_of_use[143]
2- call in __main__.example_of_use[144]
3- call in __main__[154]
4- call in class __main__.Dummy.one_method[141]
1- call in __main__.example_of_use // STACK: callerName.py[155]
2- call in __main__.example_of_use // STACK: callerName.py[155]
3- call in __main__ // STACK: callerName.py[155]
4- call in class __main__.Dummy.one_method // STACK: callerName.py[155] callerName.py[147]
"""


# here default caller_name is user choice...
caller_name = caller_name_simple     # not so verbose
# caller_name = caller_name_stack    # more verbose, with stack
