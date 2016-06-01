#!/bin/bash

echo "###############################################"
echo "CASCADE" $VERSION
echo "###############################################"

rm -Rf $PRODUCT_INSTALL

echo
echo "*** build_configure"
./build_configure
if [ $? -ne 0 ]
then
    echo "ERROR on build_configure"
    exit 1
fi

echo
echo "*** configure"
./configure \
    --without-tcl --without-tk --disable-draw \
    --with-freetype=$FREETYPEDIR \
    --enable-debug=no --enable-production=yes \
    --with-gl2ps=$GL2PSDIR \
    --with-freeimage=$FREEIMAGEDIR \
    --prefix=$PRODUCT_INSTALL

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

