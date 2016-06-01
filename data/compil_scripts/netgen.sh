#!/bin/bash

echo "##########################################################################"
echo "netgen" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** configure"
BFLAG="-m64"
OLEVEL="-O2"
echo ./configure --prefix=${PRODUCT_INSTALL} \
    --with-occ=${CASROOT} \
    --with-tcl=${TCLHOME}/lib \
    --with-tk=${TCLHOME}/lib \
    --with-togl=${TCLHOME}/lib \
    LDFLAGS="-L${TCLHOME}/lib" \
    CPPFLAGS="-I${TCLHOME}/include" \
    CXXFLAGS="${OLEVEL} ${BFLAG}"
./configure --prefix=${PRODUCT_INSTALL} \
    --with-occ=${CASROOT} \
    --with-tcl=${TCLHOME}/lib \
    --with-tk=${TCLHOME}/lib \
    --with-togl=${TCLHOME} \
    LDFLAGS="-L${TCLHOME}/lib" \
    CPPFLAGS="-I${TCLHOME}/include" \
    CXXFLAGS="${OLEVEL} ${BFLAG}"
if [ $? -ne 0 ]
then
    echo "error on configure"
    exit 1
fi

echo
echo "*** compile"
make
if [ $? -ne 0 ]
then
    echo "error on make"
    exit 2
fi

echo
echo "*** install"
make install
if [ $? -ne 0 ]
then
    echo "error on make install"
    exit 3
fi

echo
echo "*** copy headers"
for directory in general gprim linalg meshing ; do
    cp -vf ${PRODUCT_BUILD}/libsrc/${directory}/*.hpp ${PRODUCT_INSTALL}/include
done
cp -vf ${PRODUCT_BUILD}/libsrc/include/mystdlib.h ${PRODUCT_BUILD}/libsrc/include/mydefs.hpp ${PRODUCT_INSTALL}/include
cp -vf ${PRODUCT_BUILD}/libsrc/occ/occ*.hpp ${PRODUCT_INSTALL}/include


echo
echo "########## END"
