#!/bin/bash

echo "##########################################################################"
echo "libxml2" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

export LDFLAGS=-L$PYTHON_ROOT_DIR/lib

echo
echo "*** autogen"
$SOURCE_DIR/autogen.sh

echo
echo "*** configure"
$SOURCE_DIR/configure --with-python=${PYTHON_ROOT_DIR} --prefix=$PRODUCT_INSTALL
if [ $? -ne 0 ]
then
    echo "ERROR on configure"
    exit 1
fi

if [[ $DIST_NAME == "MG" ]]
then
    export PYTHON_LIBS="-L${PYTHON_ROOT_DIR}/lib"
fi

echo
echo "*** make" $MAKE_OPTIONS
make -d $MAKE_OPTIONS
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
echo "*** install python"
PWD = `pwd`
cd python
CFLAGS=-I${PWD}/include ${PYTHON_ROOT_DIR}/bin/python setup.py build
CFLAGS=-I${PWD}/include ${PYTHON_ROOT_DIR}/bin/python setup.py install

echo
echo "########## END"

