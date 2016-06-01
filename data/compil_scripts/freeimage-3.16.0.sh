#!/bin/bash

echo "###############################################"
echo "freeimage" $VERSION
echo "###############################################"

cp -r $SOURCE_DIR/* .

# hack pour CO5.5
if [[ $DIST_NAME == "CO" && $DIST_VERSION == "5.5" ]] 
then
	export CC=/usr/bin/gcc44
fi


rm -Rf $PRODUCT_INSTALL
echo -n ".. Patching freeimage sources: fix build procedure..." && \
		sed -i "s%DESTDIR ?= /%DESTDIR ?= /usr%g;s%INCDIR ?= \$(DESTDIR)/usr/include%INCDIR ?= \$(DESTDIR)/include%g;s%INSTALLDIR ?= \$(DESTDIR)/usr/lib%INSTALLDIR ?= \$(DESTDIR)/lib%g;s%-o root -g root %%g" Makefile.gnu >& /dev/null && \
		sed -i "s%DESTDIR ?= /%DESTDIR ?= /usr%g;s%INCDIR ?= \$(DESTDIR)/usr/include%INCDIR ?= \$(DESTDIR)/include%g;s%INSTALLDIR ?= \$(DESTDIR)/usr/lib%INSTALLDIR ?= \$(DESTDIR)/lib%g;s%-o root -g root %%g" Makefile.fip >& /dev/null
	    if [ "$?" != "0" ] ; then
		echo
		echo "Error: problem patching freeimage sources"
		echo
		return 1
	    fi
	    echo "OK"

	    echo -n ".. Patching freeimage sources: gcc 4.7 compatibility..." && \
		sed -i 's%\(#include "OpenEXRConfig.h"\)%\1\n#include <string.h>%g' Source/OpenEXR/IlmImf/ImfAutoArray.h
	    if [ "$?" != "0" ] ; then
		echo
		echo "Error: problem patching freeimage sources"
		echo
	    fi
	    echo "OK"

echo
echo "*** FreeImage: make" $MAKE_OPTIONS
make -f Makefile.gnu
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "*** FreeImage: make install"
make -f Makefile.gnu DESTDIR=$PRODUCT_INSTALL install
if [ $? -ne 0 ]
then
    echo "ERROR on make install"
    exit 3
fi

echo
echo "*** FreeImage: make clean"
make -f Makefile.gnu clean

echo
echo "*** FreeImagePlus: make" $MAKE_OPTIONS
make -f Makefile.fip
if [ $? -ne 0 ]
then
    echo "ERROR on make"
    exit 2
fi

echo
echo "*** FreeImagePlus: make install"
make -f Makefile.fip DESTDIR=$PRODUCT_INSTALL install
if [ $? -ne 0 ]
then
    echo "ERROR on make install"
    exit 3
fi

echo
echo "*** FreeImagePlus: make clean"
make -f Makefile.fip clean

echo
echo "########## END"

