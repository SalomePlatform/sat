dnl  Copyright (C) 2007-2010  CEA/DEN, EDF R&D, OPEN CASCADE
dnl
dnl  Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
dnl  CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
dnl
dnl  This library is free software; you can redistribute it and/or
dnl  modify it under the terms of the GNU Lesser General Public
dnl  License as published by the Free Software Foundation; either
dnl  version 2.1 of the License.
dnl
dnl  This library is distributed in the hope that it will be useful,
dnl  but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
dnl  Lesser General Public License for more details.
dnl
dnl  You should have received a copy of the GNU Lesser General Public
dnl  License along with this library; if not, write to the Free Software
dnl  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
dnl
dnl  See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
dnl

#  Check availability of :sat:{PYCMP} binary distribution
#
#  Author : Marc Tajchman (CEA, 2002)
#------------------------------------------------------------

AC_DEFUN([CHECK_:sat:{PYCMP}],[

AC_CHECKING(for :sat:{PYCMP})

:sat:{PYCMP}_ok=no

AC_ARG_WITH(:sat:{PYCMP},
	    --with-:sat:{PYCMP_minus}=DIR root directory path of :sat:{PYCMP} installation,
	    :sat:{PYCMP}_DIR="$withval",:sat:{PYCMP}_DIR="")

if test "x$:sat:{PYCMP}_DIR" = "x" ; then

# no --with-:sat:{PYCMP_minus} option used

  if test "x$:sat:{PYCMP}_ROOT_DIR" != "x" ; then

    # :sat:{PYCMP}_ROOT_DIR environment variable defined
    :sat:{PYCMP}_DIR=$:sat:{PYCMP}_ROOT_DIR

  else

    # search :sat:{PYCMP} binaries in PATH variable
    AC_PATH_PROG(TEMP, :sat:{PYCMP}GUI.py)
    if test "x$TEMP" != "x" ; then
      :sat:{PYCMP}_BIN_DIR=`dirname $TEMP`
      :sat:{PYCMP}_DIR=`dirname $:sat:{PYCMP}_BIN_DIR`
    fi

  fi
#
fi

if test -f ${:sat:{PYCMP}_DIR}/bin/salome/:sat:{PYCMP}GUI.py  ; then
  :sat:{PYCMP}_ok=yes
  AC_MSG_RESULT(Using :sat:{PYCMP} distribution in ${:sat:{PYCMP}_DIR})

  if test "x$:sat:{PYCMP}_ROOT_DIR" == "x" ; then
    :sat:{PYCMP}_ROOT_DIR=${:sat:{PYCMP}_DIR}
  fi
  AC_SUBST(:sat:{PYCMP}_ROOT_DIR)
else
  AC_MSG_WARN("Cannot find compiled $:sat:{PYCMP} distribution")
fi
  
AC_MSG_RESULT(for :sat:{PYCMP}: :sat:{PYCMP}_ok)
 
])dnl
 
