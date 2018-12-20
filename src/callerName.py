#!/usr/bin/env python
#-*- coding:utf-8 -*-

# https://gist.github.com/techtonik/2151727
# Public Domain, i.e. feel free to copy/paste
# Considered a hack in Python 2

import inspect
import logging
import sys


def caller_name(skip=1):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

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
    lineno = inspect.currentframe().f_back.f_back.f_lineno
    if codename != '<module>':  # top level usually
        name.append(codename + "[%s]" % str(lineno))  # function or a method
    del parentframe
    return ".".join(name)