#!/bin/bash

echo "##########################################################################"
echo "cmake" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

echo
echo "*** bootstrap"
$SOURCE_DIR/bootstrap --prefix=${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on bootstrap"
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

