#!/bin/bash

echo "##########################################################################"
echo "hdf5" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

CMAKE_OPTIONS=""
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_INSTALL_PREFIX:STRING=${PRODUCT_INSTALL}"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DCMAKE_BUILD_TYPE:STRING=Release"
#CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_USE_16_API_DEFAULT:BOOL=ON"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DBUILD_SHARED_LIBS:BOOL=ON"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_ALLOW_EXTERNAL_SUPPORT:BOOL=ON"
CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_BUILD_HL_LIB:BOOL=ON"


if [ -n "$MPI_ROOT" ]
then
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_ENABLE_PARALLEL:BOOL=ON"
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_BUILD_CPP_LIB:BOOL=OFF"
else
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_ENABLE_PARALLEL:BOOL=OFF"
    CMAKE_OPTIONS=$CMAKE_OPTIONS" -DHDF5_BUILD_CPP_LIB:BOOL=ON"
fi


echo
echo "*** cmake" $CMAKE_OPTIONS
cmake $CMAKE_OPTIONS $SOURCE_DIR
if [ $? -ne 0 ]
then
    echo "ERROR on CMake"
    exit 1
fi

if [ -n "$MPI_ROOT" ]
then
    sed -e 's/;//' -i src/CMakeFiles/H5make_libsettings.dir/link.txt
    sed -e 's/;//' -i src/CMakeFiles/H5detect.dir/link.txt
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

