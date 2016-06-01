#!/bin/bash

echo "##########################################################################"
echo "MeshGems" $VERSION
echo "##########################################################################"

echo
echo "*** mkdir" $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL
if [ $? -ne 0 ]
then
    echo "ERROR on mkdir"
    exit 1
fi

echo
echo "*** cp -r "$SOURCE_DIR"/* " $PRODUCT_INSTALL
cp -r $SOURCE_DIR/* $PRODUCT_INSTALL
if [ $? -ne 0 ]
then
    echo "ERROR on cp"
    exit 2
fi

echo
echo "########## END"

