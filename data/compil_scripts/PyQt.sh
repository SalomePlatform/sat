#!/bin/bash

echo "##########################################################################"
echo "PyQt" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

python_name=python$PYTHON_VERSION

echo
echo "*** configure"
python $SOURCE_DIR/configure.py --confirm-license --no-designer-plugin \
    --bindir=${PRODUCT_INSTALL}/bin \
    --destdir=${PRODUCT_INSTALL}/lib/$python_name/site-packages \
    --sipdir=${PRODUCT_INSTALL}/sip \
    --plugin-destdir=${PRODUCT_INSTALL}/qt 2>&1
if [ $? -ne 0 ]
then
    echo "ERROR on configure"
    exit 1
fi

echo
echo "*** make" $MAKE_OPTIONS
make $MAKE_OPTIONS
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
echo "########## END"

