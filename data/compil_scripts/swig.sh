#!/bin/bash

echo "##########################################################################"
echo "swig" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

#echo
#echo "*** autogen"
#./autogen.sh
#if [ $? -ne 0 ]
#then
#    echo "ERROR on autogen"
#    exit 1
#fi

echo
echo "*** configure"
$SOURCE_DIR/configure --prefix=${PRODUCT_INSTALL} --without-pcre --without-octave
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
echo "*** link swig2.0 -> swig"
cd $PRODUCT_INSTALL/bin
ln -s swig swig2.0
if [ $? -ne 0 ]
then
    echo "ERROR on link swig2.0 -> swig"
    exit 4
fi

echo
echo "########## END"

