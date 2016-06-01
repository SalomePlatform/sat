#!/bin/bash

echo "##########################################################################"
echo "Sphinx" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

mkdir -p ${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages
PYTHONPATH=${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages:${PYTHONPATH}

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
echo "*** fix binaires"
PYTHON_BIN="${PYTHONHOME}/bin/python"
echo "Replace '#!${PYTHON_BIN}' with '#!/usr/bin/env python'"
sed -i "s|#!${PYTHON_BIN}|#!/usr/bin/env python|g" ${PRODUCT_INSTALL}/bin/*

echo
echo "########## END"

