#!/bin/bash

echo "##########################################################################"
echo "tcl" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

echo
echo "*** configure"
$SOURCE_DIR/unix/configure --prefix=$PRODUCT_INSTALL --enable-shared --enable-threads
if [ $? -ne 0 ]
then
    echo "ERROR on configure"
    exit 1
fi

echo
echo "*** make" $MAKE_OPTIONS
make $MAKE_OPTIONS
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "*** make install"
make install
if [ $? -ne 0 ]
then
    echo "ERROR on make install"
    exit 3
fi

echo
echo "########## END"

