
"""
import os
import gettext

# get path to salomeTools sources
satdir  = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
srcdir = os.path.join(satdir, 'src')
cmdsdir = os.path.join(satdir, 'commands')

# load resources for internationalization
gettext.install("salomeTools", os.path.join(srcdir, "i18n"))

import application
import check
import clean
import compile
import config
import configure
import doc
import environ
import find_duplicates
import generate
import init
import job
import jobs
import launcher
import log
import make
import makeinstall
import package
import patch
import prepare
import profile
import run
import script
import shell
import source
import template
import test
"""
