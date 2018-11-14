#!/bin/env python

"""
create fr/LC_MESSAGES/salomeTools.mo from r/LC_MESSAGES/salomeTools.po
"""

import polib
po = polib.pofile('fr/LC_MESSAGES/salomeTools.po', encoding='utf-8')
po.save_as_mofile('fr/LC_MESSAGES/salomeTools.mo')
