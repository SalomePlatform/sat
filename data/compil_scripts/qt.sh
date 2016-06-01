#!/bin/bash

echo "##########################################################################"
echo "Qt" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

cp -r $SOURCE_DIR/* .

echo
echo "*** configure"
CXXFLAGS="-fpermissive" ./configure -prefix $PRODUCT_INSTALL -release -opensource -no-rpath \
    -verbose -no-separate-debug-info -confirm-license -qt-libpng -no-sql-cli
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

echo "*** create link for lib64"
cd $PRODUCT_INSTALL
ln -s lib lib64


echo "*** correction of a problem with webcore and jscore libraries"
cd ${PRODUCT_INSTALL}/lib && sed -i "s% -L../../WebCore/release%%g;s% -L../../JavaScriptCore/release%%g;s% -lwebcore%%g;s% -ljscore%%g" libQtWebKit.la

echo "*** Adding qt.conf file in order to be able to compile using the moved Qt installation"
cd ${PRODUCT_INSTALL}/bin && echo -e "[Paths]\nPrefix=..\nBinaries=bin" > qt.conf

echo
echo "########## END"

