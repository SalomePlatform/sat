#!/bin/bash

echo "##########################################################################"
echo "med" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

CMAKE_OPTIONS=""
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_INSTALL_PREFIX:STRING=${PRODUCT_INSTALL}"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_BUILD_TYPE:STRING=Release"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DMEDFILE_BUILD_STATIC_LIBS:BOOL=OFF"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DMEDFILE_BUILD_SHARED_LIBS:BOOL=ON"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_ROOT_DIR:STRING=${HDF5_ROOT_DIR}"

if [ -n "$MPI_ROOT" ]
then
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DMEDFILE_USE_MPI:BOOL=ON"
else
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DMEDFILE_USE_MPI:BOOL=OFF"
fi

mkdir BUILD
cd BUILD

cmake $CMAKE_OPTIONS $SOURCE_DIR

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

