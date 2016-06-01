#!/bin/bash

echo "##########################################################################"
echo "tk" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp $TCLHOME/include/*.h generic/

echo
echo "*** configure"
$SOURCE_DIR/unix/configure --prefix=$TCLHOME --enable-shared --enable-threads \
    --with-tcl=$TCLHOME/lib --with-tclinclude=$TCLHOME/include
if [ $? -ne 0 ]
then
    echo "ERROR on configure"
    exit 2
fi

echo
echo "*** make"
make
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

mkdir -p $PRODUCT_INSTALL
echo "Tk is installed into tcl dir $TCLHOME" > $PRODUCT_INSTALL/README
cp tkConfig.sh $TCLHOME/lib #Needed fot netgen

echo
echo "########## END"

