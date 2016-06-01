#!/bin/bash

echo "##########################################################################"
echo "cython" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

echo `pwd`
echo  "*** copy sources in BUILD directory"
cp -r $SOURCE_DIR/* .

echo
echo "*** setup.py BUILD"
python setup.py build
if [ $? -ne 0 ]
then
    echo "ERROR on build"
    exit 2
fi

mkdir -p $PRODUCT_INSTALL
echo
echo "*** install"
python setup.py install --prefix=$PRODUCT_INSTALL
if [ $? -ne 0 ]
then
    echo "ERROR on install"
    exit 3
fi

echo
echo "########## END"
