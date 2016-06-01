#!/bin/bash

echo "##########################################################################"
echo "setuptools" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

mkdir -p ${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages
export PYTHONPATH=${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages:${PYTHONPATH}

cp -r $SOURCE_DIR/* .

# unset PYTHONDONTWRITEBYTECODE set by default on MD10
PYTHONDONTWRITEBYTECODE=

echo
echo "*** setup.py"
python setup.py install --prefix=${PRODUCT_INSTALL} --install-lib ${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages
if [ $? -ne 0 ]
then
    echo "ERROR on setup"
    exit 3
fi

echo
echo "########## END"

