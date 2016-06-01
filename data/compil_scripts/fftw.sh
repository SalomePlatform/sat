#!/bin/bash

echo "##########################################################################"
echo "fftw" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** configure"
./configure --prefix=$PRODUCT_INSTALL --enable-shared --disable-static
if [ $? -ne 0 ]
then
    echo "ERROR on fftw"
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
