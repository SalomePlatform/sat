dnl Copyright (C) 2007-2011  CEA/DEN, EDF R&D, OPEN CASCADE
dnl
dnl Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
dnl CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
dnl
dnl This library is free software; you can redistribute it and/or
dnl modify it under the terms of the GNU Lesser General Public
dnl License as published by the Free Software Foundation; either
dnl version 2.1 of the License.
dnl
dnl This library is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
dnl Lesser General Public License for more details.
dnl
dnl You should have received a copy of the GNU Lesser General Public
dnl License along with this library; if not, write to the Free Software
dnl Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
dnl
dnl See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
dnl

## ------------------------
## Python file handling
## From Andrew Dalke
## Modified by Marc Tajchman (06/2001)
## ------------------------

dnl CHECK_PYTHON([module, classes])
dnl
dnl Adds support for distributing Python modules or classes.
dnl Python library files distributed as a `module' are installed
dnl under PYTHON_SITE_PACKAGE (eg, ./python1.5/site-package/package-name)
dnl while those distributed as `classes' are installed under PYTHON_SITE
dnl (eg, ./python1.5/site-packages).  The default is to install as
dnl a `module'.

AC_DEFUN([CHECK_PYTHON],
 [
  python_ok=yes
 
  AC_ARG_WITH(python,
   [AC_HELP_STRING([--with-python=DIR],[root directory path of python installation])],
   [PYTHON="$withval/bin/python"
    AC_MSG_RESULT("select python distribution in $withval")
   ], [
    AC_PATH_PROG(PYTHON, python)
    ])
  
  AC_CHECKING([local Python configuration])

  AC_REQUIRE([AC_LINKER_OPTIONS])dnl

  PYTHON_PREFIX=`echo $PYTHON | sed -e "s,[[^/]]*$,,;s,/$,,;s,^$,.,"`
  PYTHON_PREFIX=`echo $PYTHON_PREFIX | sed -e "s,[[^/]]*$,,;s,/$,,;s,^$,.,"`
  PYTHONHOME=$PYTHON_PREFIX

  AC_SUBST(PYTHON_PREFIX)
  AC_SUBST(PYTHONHOME)

  changequote(<<, >>)dnl
  PYTHON_VERSION=`$PYTHON -c "import sys; print sys.version[:3]"`
  changequote([, ])dnl
  AC_SUBST(PYTHON_VERSION)

  PY_MAKEFILE=${PYTHON_PREFIX}/lib${LIB_LOCATION_SUFFIX}/python$PYTHON_VERSION/config/Makefile
  if test ! -f "$PY_MAKEFILE"; then
    if test "${build_cpu::6}" = "x86_64" ; then
      PY_MAKEFILE=${PYTHON_PREFIX}/lib64/python$PYTHON_VERSION/config/Makefile
    fi
  fi
  if test ! -f "$PY_MAKEFILE"; then
     AC_MSG_WARN([*** Couldn't find ${PY_MAKEFILE}.  Maybe you are
*** missing the development portion of the python installation])
     python_ok=no
  fi

  AC_SUBST(PYTHON_INCLUDES)
  AC_SUBST(PYTHON_LIBS)

  PYTHON_INCLUDES=-I$PYTHON_PREFIX/include/python$PYTHON_VERSION
  PYTHON_LIBS="-L${PYTHON_PREFIX}/lib${LIB_LOCATION_SUFFIX}/python${PYTHON_VERSION}/config -lpython${PYTHON_VERSION}"
  PYTHON_LIB=$PYTHON_LIBS
  PYTHON_LIBA=${PYTHON_PREFIX}/lib${LIB_LOCATION_SUFFIX}/python$PYTHON_VERSION/config/libpython$PYTHON_VERSION.a
  if test "${build_cpu::6}" = "x86_64" ; then
    if test "$PY_MAKEFILE" = "${PYTHON_PREFIX}/lib64/python$PYTHON_VERSION/config/Makefile" ; then
      PYTHON_LIBS="-L${PYTHON_PREFIX}/lib64/python${PYTHON_VERSION}/config -lpython${PYTHON_VERSION}"
      PYTHON_LIB=$PYTHON_LIBS
      PYTHON_LIBA=${PYTHON_PREFIX}/lib64/python$PYTHON_VERSION/config/libpython$PYTHON_VERSION.a
    fi
  fi

  dnl At times (like when building shared libraries) you may want
  dnl to know which OS Python thinks this is.

  AC_SUBST(PYTHON_PLATFORM)
  PYTHON_PLATFORM=`$PYTHON -c "import sys; print sys.platform"`

  AC_SUBST(PYTHON_SITE)
  AC_ARG_WITH(python-site,
    [AC_HELP_STRING([--with-python-site=DIR],
       [Use DIR for installing platform independent Python site-packages])],

dnl modification : by default, we install python script in salome root tree

dnl [PYTHON_SITE="$withval"
dnl python_site_given=yes],
dnl [PYTHON_SITE=$PYTHON_PREFIX"/lib/python"$PYTHON_VERSION/site-packages
dnl python_site_given=no]

   [PYTHON_SITE="$withval"
    python_site_given=yes],
   [PYTHON_SITE=${prefix}"/lib${LIB_LOCATION_SUFFIX}/python"${PYTHON_VERSION}/site-packages
    python_site_given=no])

  AC_SUBST(PYTHON_SITE_PACKAGE)
  PYTHON_SITE_PACKAGE=$PYTHON_SITE/$PACKAGE


  dnl Get PYTHON_SITE from --with-python-site-exec or from
  dnl --with-python-site or from running Python

  AC_SUBST(PYTHON_SITE_EXEC)
  AC_ARG_WITH(python-site-exec,
    [AC_HELP_STRING([--with-python-site-exec=DIR],
                    [Use DIR for installing platform dependent Python site-packages])],
    [PYTHON_SITE_EXEC="$withval"],
    [if test "$python_site_given" = yes; then
       PYTHON_SITE_EXEC=$PYTHON_SITE
     else
       PYTHON_SITE_EXEC=${PYTHON_EXEC_PREFIX}"/lib${LIB_LOCATION_SUFFIX}/python"${PYTHON_VERSION}/site-packages
     fi])

  dnl Set up the install directory
  ifelse($1, classes,
[PYTHON_SITE_INSTALL=$PYTHON_SITE],
[PYTHON_SITE_INSTALL=$PYTHON_SITE_PACKAGE])
  AC_SUBST(PYTHON_SITE_INSTALL)

  dnl Also lets automake think PYTHON means something.

  pythondir=${PYTHON_PREFIX}"/lib${LIB_LOCATION_SUFFIX}/python"${PYTHON_VERSION}/
  AC_SUBST(pythondir)

 AC_MSG_CHECKING([if we need libdb])
 PY_NEEDOPENDB=`nm $PYTHON_LIBA | grep dbopen | grep U`
  if test "x$PY_NEEDOPENDB" != "x"; then
     AC_MSG_RESULT(yes)
     AC_CHECK_LIB(db,dbopen,PYTHON_LIBS="$PYTHON_LIBS -ldb",db_ok=no)
  else
     AC_MSG_RESULT(no)
  fi

 AC_MSG_CHECKING([if we need libdl])
  PY_NEEDOPENDL=`nm $PYTHON_LIBA | grep dlopen | grep U`
  if test "x$PY_NEEDOPENDL" != "x"; then
     AC_MSG_RESULT(yes)
     AC_CHECK_LIB(dl,dlopen,PYTHON_LIBS="$PYTHON_LIBS -ldl",dl_ok=no)
  else
     AC_MSG_RESULT(no)
  fi

 AC_MSG_CHECKING([if we need libutil])
  PY_NEEDOPENPTY=`nm $PYTHON_LIBA | grep openpty | grep U`
  if test "x$PY_NEEDOPENPTY" != "x"; then
     AC_MSG_RESULT(yes)
     AC_CHECK_LIB(util,openpty,PYTHON_LIBS="$PYTHON_LIBS -lutil",openpty_ok=no)
  else
     AC_MSG_RESULT(no)
  fi

 AC_MSG_CHECKING([if we need tcltk])
  PY_NEEDTCLTK=`nm $PYTHON_LIBA | grep Tcl_Init | grep U`
  if test "x$PY_NEEDTCLTK" != "x"; then
     AC_MSG_RESULT(yes)
     AC_CHECK_LIB(tcl,Tcl_Init,PYTHON_LIBS="$PYTHON_LIBS -ltcl -ltk",tclinit_ok=no)
  else
     AC_MSG_RESULT(no)
  fi

  if test "$python_ok" == "yes"; then
      AC_MSG_RESULT(looks good)
  fi
])
