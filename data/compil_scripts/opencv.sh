#!/bin/bash

echo "##########################################################################"
echo "opencv" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

CMAKE_OPTIONS=""
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_INSTALL_PREFIX:STRING=${PRODUCT_INSTALL}"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_BUILD_TYPE:STRING=Release"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DWITH_CUDA:BOOL=OFF"

mkdir BUILD
cd BUILD

# hack pour CO5.5
if [[ $DIST_NAME == "CO" && $DIST_VERSION == "5.5" ]] 
then
	env CC=/usr/bin/gcc44 CXX=/usr/bin/g++44 cmake $CMAKE_OPTIONS $SOURCE_DIR
else
	cmake $CMAKE_OPTIONS $SOURCE_DIR
fi

if [ $? -ne 0 ]
then
    echo "ERROR on CMake"
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

