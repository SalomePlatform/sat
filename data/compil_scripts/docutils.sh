#!/bin/bash

echo "##########################################################################"
echo "docutil" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

mkdir -p ${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages
PYTHONPATH=${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/site-packages:${PYTHONPATH}

echo
echo "setup.py"
python setup.py install --prefix ${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on setup"
    exit 3
fi

echo
echo "########## END"

