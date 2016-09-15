#!/usr/bin/env python
#-*- coding:utf-8 -*-

# This script can be used to generate resources (splash screen, logo app and about screen)
# to customize a SALOME application.

import os, sys
try:
    import Image
    import ImageDraw
    import ImageFont
except ImportError, exc:
    print
    print "** Error in %s" % os.path.realpath(__file__)
    print "This script requires the Image, ImageDraw and ImageFont libraries"
    print exc
    sys.exit(1)

# splash screen
C_FONT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xirod.ttf')
C_SPLASH_WIDTH = 600
C_SPLASH_HEIGHT = 300
C_SPLASH_COLOR = (100, 155, 100)
C_LOGO_COLOR = "rgb(0, 0, 0)"
C_BORDER = 10

##
# create the splash screen and the about logo.
def generate_splash(dest, appname, version):
    uname = unicode(appname, 'UTF-8')
    uversion = unicode(version, 'UTF-8')

    font48 = ImageFont.truetype(C_FONT_PATH, 48)
    font20 = ImageFont.truetype(C_FONT_PATH, 20)

    # create the splash screen
    im = Image.new("RGBA", (C_SPLASH_WIDTH, C_SPLASH_HEIGHT), C_SPLASH_COLOR)
    draw = ImageDraw.Draw(im)
    
    # add the name of the application
    iw, ih = draw.textsize(uname, font=font48)
    x = (C_SPLASH_WIDTH - iw) / 2.0 # horizontal center
    y = (C_SPLASH_HEIGHT - ih) / 2.0 # vertical center
    draw.text((x, y), uname, font=font48)

    # add powered by SALOME
    iw, ih = draw.textsize("Powered by SALOME", font=font20)
    draw.text((C_BORDER, C_SPLASH_HEIGHT - C_BORDER - ih), "Powered by SALOME", font=font20)

    # add the version if any
    if len(version) > 0:
        iw, ih = draw.textsize(uversion, font=font20)
        draw.text((C_SPLASH_WIDTH - C_BORDER - iw, C_SPLASH_HEIGHT - C_BORDER - ih), uversion, font=font20)

    del draw
    im.save(os.path.join(dest, 'splash.png'), "PNG")
    im.save(os.path.join(dest, 'about.png'), "PNG")

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
    draw.text((0, 0), uname, font=font, fill=C_LOGO_COLOR)
    del draw
    im.save(os.path.join(dest, 'applogo.png'), "PNG")


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "usage: %s <dest> <name> [<version>]" % sys.argv[0]
        sys.exit(1)

    dest = sys.argv[1]
    appname = sys.argv[2]
    version = ""
    if len(sys.argv) > 3: version = sys.argv[3]
    
    generate_splash(dest, appname, version)
    generate_logo(dest, appname)
