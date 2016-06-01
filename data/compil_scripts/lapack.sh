#!/bin/bash

echo "##########################################################################"
echo "lapack" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

#echo "copy file"
cp make.inc.example make.inc

mkdir -p $PRODUCT_INSTALL
cp -rp $SOURCE_DIR/* $PRODUCT_INSTALL/


CMAKE_OPTIONS="$SOURCE_DIR"
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DCMAKE_INSTALL_PREFIX=$PRODUCT_INSTALL"
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DCMAKE_BUILD_TYPE=Release" 
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DBUILD_SHARED_LIBS:BOOL=ON"
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DCMAKE_CXX_FLAGS=-fPIC"
CMAKE_OPTIONS="${CMAKE_OPTIONS} -DCMAKE_C_FLAGS=-fPIC"

echo
echo "*** cmake ${CMAKE_OPTIONS}"
cmake ${CMAKE_OPTIONS}
if [ $? -ne 0 ]
then
    echo "ERROR on cmake"
    exit 1
fi

echo
echo "*** make"
make
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "*** make install"

make install

#cp lib/libblas.so $PRODUCT_INSTALL/lib/
#cp lib/liblapack.so $PRODUCT_INSTALL/lib/
#cp lib/libtmglib.so $PRODUCT_INSTALL/lib/

#ln -s $PRODUCT_INSTALL/lib/blas_LINUX.so $PRODUCT_INSTALL/lib/libblas.so
#ln -s $PRODUCT_INSTALL/lib/lapack_LINUX.so $PRODUCT_INSTALL/lib/liblapack.so

if [ $? -ne 0 ]
then
    echo "ERROR on make install"
    exit 3
fi


#echo
#echo "*** make"
#make blaslib
#if [ $? -ne 0 ]
#then
#    echo "ERROR on make"
#    exit 2
#fi

#make lapacklib
#if [ $? -ne 0 ]
#then
#    echo "ERROR on make"
#    exit 2
#fi
##ln -s blas_LINUX.a libblas.a
##ln -s lapack_LINUX.a liblapack.a

#ln -s librefblas.a libblas.a

echo
echo "########## END"

