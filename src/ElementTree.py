

"""
using VERSION 1.3.0 native xml.etree.ElementTree for python3
appending method tostring serialize 'pretty_xml'
"""

import sys
import debug as DBG

_versionPython = sys.version_info[0]

if _versionPython < 3:
  # python2 previous historic mode
  import src.ElementTreePython2 as etree
  DBG.write("ElementTree Python2 %s" % etree.VERSION, etree.__file__, DBG.isDeveloper())
  tostring = etree.tostring

else:
  # python3 mode
  # import xml.etree.ElementTree as etree # native version
  import src.ElementTreePython3 as etree # VERSION 1.3.0 plus _serialize 'pretty_xml'
  DBG.write("ElementTree Python3 %s" % etree.VERSION, etree.__file__, DBG.isDeveloper())

  def tostring(node, encoding='utf-8'):
    """
    fix output as str with encoding='unicode' because python3
    If encoding is "unicode", a string is returned.
    Otherwise a bytestring is returned
    """
    try:
      aStr = etree.tostring(node, encoding='unicode', method="pretty_xml")
    except:
      print("*****************************\n problem node", node)
      # try no pretty
      aStr = etree.tostring(node, encoding='unicode')
    # if be byte
    # aStr = aStr.decode('utf-8')
    return aStr

# common use
Element = etree.Element
parse = etree.parse

