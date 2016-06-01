#!/bin/bash

echo "##########################################################################"
echo "matplotlib" $VERSION
echo "##########################################################################"

rm -rf $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL
echo
echo "*** setup.py"

cp -r $SOURCE_DIR/* .

# Making a directory that will be used in install
BUILD_DIR=`pwd`
cd $PRODUCT_INSTALL
mkdir -p lib/python2.7/site-packages
cd $BUILD_DIR
# Hack PYTHONPATH in order to make 'setup.py install' believe that PRODUCT_INSTALL is in PYTHONPATH
PYTHONPATH_SAVE=$PYTHONPATH
export PYTHONPATH=${PRODUCT_INSTALL}/lib/python2.7/site-packages:$PYTHONPATH


echo "*** setup.py BUILD"

python setup.py build

echo "*** setup.py INSTALL"

python setup.py install --prefix=${PRODUCT_INSTALL}

if [ $? -ne 0 ]
then
    export PYTHONPATH=$PYTHONPATH_SAVE
    echo "ERROR on setup"
    exit 3
fi
export PYTHONPATH=$PYTHONPATH_SAVE

echo
echo "########## END"

