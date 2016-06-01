#!/bin/bash

echo "##########################################################################"
echo "BOOST" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cd $SOURCE_DIR

if [ -n "$MPI_ROOT" ]
then
    cp tools/build/v2/user-config.jam .
    echo "using mpi ;" >> user-config.jam
fi

echo
echo "*** bootstrap.sh"
./bootstrap.sh --prefix=$PRODUCT_INSTALL
if [ $? -ne 0 ]
then
    echo "ERROR on bootstrap"
    exit 1
fi

echo "*** bjam install"
if [ -n "$MPI_ROOT" ]
then
    ./bjam --user-config=user-config.jam --layout=tagged install
else
    ./bjam install
fi
if [ $? -ne 0 ]
then
    echo "ERROR on bjam install"
    exit 3
fi

echo
echo "########## END"
