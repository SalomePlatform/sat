#!/bin/bash

echo "##########################################################################"
echo "ParMetis" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** apply sed for 64bits platforms"
sed -e 's/CC = mpicc/CC = mpicc -fPIC/g' Makefile.in > Makefile.in_new
cp Makefile.in_new Makefile.in

echo
echo "*** make" $MAKE_OPTIONS
make $MAKE_OPTIONS
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

# install
echo "** install"
mkdir -p $PRODUCT_INSTALL
mkdir -p $PRODUCT_INSTALL"/METISLib"
mkdir -p $PRODUCT_INSTALL"/ParMETISLib"

cp libparmetis.a $PRODUCT_INSTALL
cp libmetis.a $PRODUCT_INSTALL
cp parmetis.h $PRODUCT_INSTALL
cp Graphs/ptest Graphs/mtest Graphs/parmetis Graphs/pometis $PRODUCT_INSTALL

cp METISLib/*.h $PRODUCT_INSTALL"/METISLib"
cp ParMETISLib/*.h $PRODUCT_INSTALL"/ParMETISLib"

echo
echo "########## END"

