#!/bin/bash

echo "##########################################################################"
echo "Python" $VERSION
echo "##########################################################################"

rm -Rf $PRODUCT_INSTALL

# WARNING $PYTHOSTARTUP can be problematic -> unset.
# If an error occurs during make install then the environement is "messy"

# check for readline library
# if NO_CHECK_READLINE is not set and readline is not found the script will exit
if [[ "x$NO_CHECK_READLINE" == "x" ]]
then
    echo
    echo "*** check for readline library"
    python -c "import readline" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "ERROR readline library is not installed"
        echo "set environement variable NO_CHECK_READLINE to skip checking for readline library"
        exit 5
    else
        echo "readline library found"
    fi
fi

echo
echo "*** configure"
if [[ $DIST_NAME == "UB" ]]
then
    export LDFLAGS="-L/usr/lib/x86_64-linux-gnu/"
    echo "set LDFLAGS=$LDFLAGS"
fi

################################## Hack the bug with <Lib64> on OpenSuse 
if [[ $DIST_NAME == "OS" ]]
then
    echo
    echo "*** fix bug OpenSuse"
	VAR_PWD=`pwd`
	mkdir -p ${PRODUCT_INSTALL}
	echo
	echo "*** create missing link ${PRODUCT_INSTALL}/lib ${PRODUCT_INSTALL}/lib64"
	cd ${PRODUCT_INSTALL}
	mkdir lib
	ln -s lib lib64
	cd $VAR_PWD
fi

$SOURCE_DIR/configure --prefix=$PRODUCT_INSTALL --enable-shared --with-threads --without-pymalloc --enable-unicode=ucs4
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

######### link for salome

PYTHON_VERSION=`${PRODUCT_INSTALL}/bin/python -c "import sys; print sys.version[:3]"`
if [ $? -ne 0 ]
then
    PYTHON_VERSION="${VERSION:0:3}"
fi

cd ${PRODUCT_INSTALL}/lib/python${PYTHON_VERSION}/config

if [ ! -e libpython${PYTHON_VERSION}.so ]
then
    echo
    echo "*** create missing link"
    ln -sf ../../libpython${PYTHON_VERSION}.so .
    if [ $? -ne 0 ]
    then
        echo "ERROR when creating missing link"
        # no error here
    fi
fi

# changement des ent�tes
#cd $PRODUCT_INSTALL/bin
#for sc in idle pydoc smtpd.py ; do
#    if [ -e $sc ] ; then
#   sed -e "s%#\!.*python%#\!/usr/bin/env python%" "$sc" > _"$sc"
#   mv -f _"$sc" "$sc"
#   chmod a+x "$sc"
#    fi
#done

echo
echo "########## END"

