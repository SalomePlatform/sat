#/bin/env python
import polib
po = polib.pofile('fr/LC_MESSAGES/salomeTools.po', encoding='utf-8')
po.save_as_mofile('fr/LC_MESSAGES/salomeTools.mo')
