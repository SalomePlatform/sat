#!/bin/bash

echo "##########################################################################"
echo "numpy" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL

echo
echo "*** setup.py"
## editer customize.py Pour LApack : using Atlas, Pour Blas : Using gsl
python $SOURCE_DIR/setup.py build
python $SOURCE_DIR/setup.py install --prefix=${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on setup"
    exit 3
fi

echo
echo "########## END"

