#!/bin/bash

echo "##########################################################################"
echo "graphviz" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

if [ -e ${TCLHOME}/lib64/tcl${TCL_SHORT_VERSION}/graphviz ]
then
    rm -rf ${TCLHOME}/lib64/tcl${TCL_SHORT_VERSION}/graphviz
fi

echo "graphviz compilation"
# tcl natif
if [ ${#TCLHOME} -eq 0 ]
then
    TCLHOME="/usr"
fi

echo
echo "*** ./configure --prefix=${PRODUCT_INSTALL} --with-tcl=${TCLHOME}/lib --with-expat=no --with-qt=no --with-cgraph=no  --enable-perl=no"
./configure --prefix=${PRODUCT_INSTALL} --with-tcl=${TCLHOME}/lib --with-expat=no --with-qt=no --with-cgraph=no --enable-perl=no

if [ $? -ne 0 ]
then
    echo "ERROR on configure"
    exit 1
fi

echo
echo "*** make" ${MAKE_OPTIONS}
make ${MAKE_OPTIONS}
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo "*** make install"
make install
if [ $? -ne 0 ]
then
    echo "ERROR on make install"
    exit 3
fi

echo
echo "########## END"

