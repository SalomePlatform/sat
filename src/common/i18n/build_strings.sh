#!/bin/bash

# This script gets the strings to internationalise from the source code

I18HOME=`dirname $0`
SRC_DIR=$I18HOME/../..

# get strings for french translation
echo Build strings for French

poFile=$I18HOME/fr/LC_MESSAGES/salomeTools.po
refFile=$I18HOME/fr/LC_MESSAGES/ref.pot

xgettext $SRC_DIR/*.py $SRC_DIR/common/*.py \
    --no-wrap --no-location --language=Python --omit-header \
    --output=$refFile
msgmerge -q --update $poFile $refFile
msgattrib --no-obsolete -o $poFile $poFile
rm $refFile

