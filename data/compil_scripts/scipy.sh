#!/bin/bash

echo "##########################################################################"
echo "scipy" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** build"
python setup.py build
if [ $? -ne 0 ]
then
    echo "ERROR on build"
    exit 2
fi

mkdir -p $PRODUCT_INSTALL
echo
echo "*** install"
python setup.py install --prefix=${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on install"
    exit 3
fi

#mkdir -p $PRODUCT_INSTALL
#echo "scipy is installed into python dir $PYTHON_ROOT_DIR" > $PRODUCT_INSTALL/README

echo
echo "########## END"
