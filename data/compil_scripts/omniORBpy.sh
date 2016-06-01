#!/bin/bash

echo "##########################################################################"
echo "omniORBpy" $VERSION
echo "##########################################################################"

echo
echo "*** configure"
$SOURCE_DIR/configure --prefix=${OMNIORB_ROOT_DIR}
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

mkdir -p $PRODUCT_INSTALL
echo "omniORBpy is installed into omni dir ${OMNIORB_ROOT_DIR}" > $PRODUCT_INSTALL/README

echo
echo "########## END"

