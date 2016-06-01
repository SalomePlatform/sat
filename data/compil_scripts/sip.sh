#!/bin/bash

echo "##########################################################################"
echo "sip" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

python_name=python$PYTHON_VERSION

echo
echo "*** configure"
if [[ $BITS == "64" ]]
then
    python ./configure.py -b ${PRODUCT_INSTALL}/bin \
        -d ${PRODUCT_INSTALL}/lib/${python_name}/site-packages \
        -e ${PRODUCT_INSTALL}/include/${python_name} \
        -v ${PRODUCT_INSTALL}/sip -p linux-g++-64
else
    python ./configure.py -b ${PRODUCT_INSTALL}/bin \
        -d ${PRODUCT_INSTALL}/lib/${python_name}/site-packages \
        -e ${PRODUCT_INSTALL}/include/${python_name} \
        -v ${PRODUCT_INSTALL}/sip
fi
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

