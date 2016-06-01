#!/bin/bash

echo "##########################################################################"
echo "pyreadline" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL
echo "pyreadline is a Windows porting of readline, a native module of Unix python" > $PRODUCT_INSTALL/README

echo
echo "########## END"
