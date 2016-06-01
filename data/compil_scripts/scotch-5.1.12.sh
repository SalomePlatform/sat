#!/bin/bash

echo "##########################################################################"
echo "Scotch" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

mkdir -p $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** copy BUILD to INSTALL  : cp -ar ${PRODUCT_BUILD} ${PRODUCT_INSTALL}"
cp -ar * ${PRODUCT_INSTALL}
if [ $? -ne 0 ]
then
    echo "ERROR on cp -ar ${SOURCE_DIR} ${PRODUCT_INSTALL}"
    exit 1
fi
echo "INSTALL :: ${PRODUCT_INSTALL}"

cd ${PRODUCT_INSTALL}/src

cp Make.inc/Makefile.inc.x86-64_pc_linux2 ./Makefile.inc.ori

# add pthread for gcc > 4.4
sed -e "s%LDFLAGS\([[:space:]]*\)=\([[:space:]]*\)\(.*\)%LDFLAGS\1=\2 \3 -lpthread%g" Makefile.inc.ori > Makefile.inc

# add -fPIC
sed -e 's|CFLAGS[\t ]*=|& -fPIC|g' Makefile.inc > Makefile.in_new
cp Makefile.in_new Makefile.inc

echo
echo "*** make" $MAKE_OPTIONS
make $MAKE_OPTIONS
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "########## END"

