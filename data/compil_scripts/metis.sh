#!/bin/bash

echo "##########################################################################"
echo "Metis" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** apply sed for 64bits platforms"
sed -e 's|COPTIONS =|& -fPIC|g' Makefile.in > Makefile.in_new
cp Makefile.in_new Makefile.in

echo
echo "*** make" $MAKE_OPTIONS
make $MAKE_OPTIONS
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "*** copy build to install"
cp -ar * ${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on install"
    exit 3
fi

echo
echo "*** Modification of access rights"
chmod -R g+rwX,o+rX ${PRODUCT_INSTALL}

echo
echo "########## END"

