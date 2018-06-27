#!/usr/bin/env python
#-*- coding:utf-8 -*-

# This script can be used to generate resources (splash screen, logo app and about screen)
# to customize a SALOME application.

import os, sys


try:
  __LANG__ = os.environ["LANG"] # original locale
except:
  __LANG__ = "en_US.utf8" #default

__FR__={
    "This script requires the Image, ImageDraw and ImageFont libraries":
        "Ce script a besoin de Image, ImageDraw et ImageFont python librairies",
    "WARNING: automatic filter application name for resources:":
        "ATTENTION: filtre automatique sur le nom de l'application pour les ressources:",
    "generate": "génération de",
    "in directory": "dans le répertoire",
    "Generate resources for": "Génération des ressources pour",
}

def _loc(text):
  """very easy very locale standalone translation"""
  if "FR" in __LANG__:
    try:
      return __FR__[text]
    except:
      return text
  return text

try:
    import Image
    import ImageDraw
    import ImageFont
except ImportError, exc:
    print
    print "ERROR: " + os.path.realpath(__file__)
    print _loc("This script requires the Image, ImageDraw and ImageFont libraries")
    print exc
    sys.exit(1)


# splash screen
C_FONT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xirod.ttf')
C_SPLASH_WIDTH = 600
C_SPLASH_HEIGHT = 300
C_SPLASH_COLOR = (100, 120, 160)
C_SPLASH_TEXT_COLOR = "rgb(255, 250, 250)"
C_SHADOW_COLOR = "rgb(0, 0, 0)"
C_LOGO_COLOR = "rgb(200, 200, 200)"
C_BORDER_X = 30 #50
C_BORDER_Y = 3 #30
C_SHADOW_X = 2
C_SHADOW_Y = C_SHADOW_X

##
# create the splash screen and the about logo.
def generate_splash(dest, appname, version, subtext=None):
    if subtext is None:
        subtext="Powered by SALOME"
    uname = unicode(appname, 'UTF-8')
    uversion = unicode(version, 'UTF-8')

    fontbig = ImageFont.truetype(C_FONT_PATH, 44)
    fontsmall = ImageFont.truetype(C_FONT_PATH, 16)

    # create the splash screen
    # 12 characters are maximum for for C_SPLASH_WIDTH
    nbcar = len(uname)
    WIDTH = C_SPLASH_WIDTH
    if nbcar > 12:
        WIDTH=C_SPLASH_WIDTH*nbcar/12 #a little more
    if WIDTH > 1024:
        WIDTH = 1024 #but not too big
    #im = Image.new("RGBA", (WIDTH, C_SPLASH_HEIGHT), C_SPLASH_COLOR)
    d0 = os.path.dirname(os.path.realpath(__file__))
    f0 = os.path.join(d0,"Salome6_splash_fond.png")
    #print "cvw splash2.py",f0
    im = Image.open(f0)
    im = im.resize((WIDTH, C_SPLASH_HEIGHT))
    draw = ImageDraw.Draw(im)
    
    # add the name of the application
    iw, ih = draw.textsize(uname, font=fontbig)
    x = (WIDTH - iw) / 2.0 # horizontal center
    y = (C_SPLASH_HEIGHT - ih) / 2.0 # vertical center
    draw.text((x+C_SHADOW_X, y+C_SHADOW_Y), uname, font=fontbig, fill=C_SHADOW_COLOR)
    draw.text((x, y), uname, font=fontbig, fill=C_SPLASH_TEXT_COLOR)

    # add powered by SALOME
    iw, ih = draw.textsize(subtext, font=fontsmall)
    draw.text((C_BORDER_X+C_SHADOW_X, C_SPLASH_HEIGHT+C_SHADOW_Y-C_BORDER_Y-ih),
              subtext, font=fontsmall, fill=C_SHADOW_COLOR)
    draw.text((C_BORDER_X, C_SPLASH_HEIGHT-C_BORDER_Y-ih),
              subtext, font=fontsmall, fill=C_SPLASH_TEXT_COLOR)

    # add the version if any
    if len(version) > 0:
        iw, ih = draw.textsize(uversion, font=fontsmall)
        draw.text((WIDTH+C_SHADOW_X-C_BORDER_X-iw, C_SPLASH_HEIGHT+C_SHADOW_Y-C_BORDER_Y-ih),
                  uversion, font=fontsmall, fill=C_SHADOW_COLOR)
        draw.text((WIDTH-C_BORDER_X-iw, C_SPLASH_HEIGHT-C_BORDER_Y-ih),
                  uversion, font=fontsmall, fill=C_SPLASH_TEXT_COLOR)

    del draw
    d1 = os.path.join(dest, 'icon_splash.png')
    im.save(d1, "PNG")
    d2 = os.path.join(dest, 'icon_about.png')
    im.save(d2, "PNG")
    print _loc("in directory"), os.getcwd()
    print _loc("generate"), d1
    print _loc("generate"), d2

##
# create the application logo
def generate_logo(dest, appname):
    uname = unicode(appname, 'UTF-8')

    # evaluate size before deleting draw
    im = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(C_FONT_PATH, 18)
    iw, ih = draw.textsize(uname, font=font)
    del draw

    im = Image.new("RGBA", (iw + 5, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.text((0+1, 0), uname, font=font, fill=C_SHADOW_COLOR)
    draw.text((0, -1), uname, font=font, fill=C_LOGO_COLOR)
    del draw
    d1 = os.path.join(dest, 'icon_applogo.png')
    im.save(d1, "PNG")
    print _loc("generate"), d1
   
def filter_appname(appname):
    name = appname.upper() # xirod seems not have lower character
    for i in ["_APPLICATION","_APPLI","_APP"]:
        res = name.split(i)
        if len(res) > 1:
            name = res[0]
            return name
    
    for i in ["APPLICATION_","APPLI_","APP_"]:
        res = name.split(i)
        if len(res) > 1:
            name = res[1]
            return name

    return name

if __name__ == "__main__":
    if len(sys.argv) < 3:
      print "usage: %s <dest> <name> [<version>] [<subtext>]" % sys.argv[0]
      sys.exit(1)

    dest = sys.argv[1]
    appname = sys.argv[2]
    version = ""
    subtext = None
    if len(sys.argv) > 3: version = sys.argv[3]
    if len(sys.argv) > 4: subtext = sys.argv[4]

    print
    print _loc("Generate resources for"), appname
    name = filter_appname(appname)
    if name != appname:
      print _loc("WARNING: automatic filter application name for resources:"),
      print "'%s' -> '%s'" % (appname, name)
    
    generate_splash(dest, name, version, subtext)
    generate_logo(dest, name)
    print
