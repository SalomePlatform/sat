#!/bin/bash

echo "##########################################################################"
echo "cgnslib" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

# compilation
echo "cgnslib compilation"

CMAKE_OPTIONS=""
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_INSTALL_PREFIX:STRING=${PRODUCT_INSTALL}"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_BUILD_TYPE:STRING=Release"
if [ -n "$MPI_ROOT" ]
then
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_NEEDS_MPI:BOOL=ON"
fi

echo
echo "*** cmake"
cmake $CMAKE_OPTIONS $SOURCE_DIR
if [ $? -ne 0 ]
then
    echo "ERROR on cmake"
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

