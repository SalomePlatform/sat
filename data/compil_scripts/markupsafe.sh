#!/bin/bash

echo "##########################################################################"
echo "markupsafe" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** setup.py BUILD"
python setup.py build
if [ $? -ne 0 ]
then
    echo "ERROR on build"
    exit 2
fi

dir_lib=$PRODUCT_INSTALL'/lib/python'$PYTHON_VERSION'/site-packages'

# HACK 
PYTHONPATH=$PYTHONPATH:$dir_lib

mkdir -p $PRODUCT_INSTALL
mkdir -p $dir_lib

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
