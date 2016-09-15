dnl Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE
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

#  Check availability of Salome binary distribution
#
#  Author : Marc Tajchman (CEA, 2002)
#------------------------------------------------------------

AC_DEFUN([CHECK_GUI_MODULE],[
AC_REQUIRE([AC_LINKER_OPTIONS])dnl

LightGUI_ok=no
FullGUI_ok=no

GUI_LDFLAGS=""
GUI_CXXFLAGS=""

SALOME_GUI_DIR=""

AC_ARG_WITH(gui, 
	    [--with-gui=DIR root directory path of SALOME GUI installation],
	    [],
            [with_gui=auto])

if test "${with_gui}" = "no"; then
  SalomeGUI_need=no
else
  # define SALOME_GUI_DIR
  if test "${with_gui}" = "yes" -o "${with_gui}" = "auto"; then
    SalomeGUI_need="$with_gui"
    AC_MSG_RESULT(try \${GUI_ROOT_DIR}: ${GUI_ROOT_DIR})
    if test "x${GUI_ROOT_DIR}" != "x" ; then
      # GUI_ROOT_DIR environment variable defined
      SALOME_GUI_DIR=${GUI_ROOT_DIR}
    else
      # search Salome binaries in PATH variable
      AC_PATH_PROG(TEMP, SUITApp)
      if test "x${TEMP}" != "x" ; then
        AC_MSG_RESULT(SUITApp was found at : ${TEMP})
        SALOME_BIN_DIR=`dirname ${TEMP}`
        SALOME_GUI_DIR=`cd ${SALOME_BIN_DIR}/../..; pwd`
      fi
    fi 
  else
    # GUI directory defined by user
    SalomeGUI_need=yes
    SALOME_GUI_DIR="$with_gui"
  fi

  # check GUI installation
  AC_CHECKING(for light GUI)
  if test -f ${SALOME_GUI_DIR}/bin/salome/SUITApp ; then
    LightGUI_ok=yes
    AC_MSG_RESULT(Using SALOME GUI distribution in ${SALOME_GUI_DIR})
	
    GUI_ROOT_DIR=${SALOME_GUI_DIR}

    GUI_LDFLAGS=-L${SALOME_GUI_DIR}/lib${LIB_LOCATION_SUFFIX}/salome
    GUI_CXXFLAGS=-I${SALOME_GUI_DIR}/include/salome

    AC_CHECKING(for full GUI)
    if test -f ${SALOME_GUI_DIR}/bin/salome/SALOME_Session_Server ; then
      FullGUI_ok=yes
    fi
  else
    AC_MSG_WARN("Cannot find compiled SALOME GUI distribution")
  fi
  AC_MSG_RESULT(for light GUI: ${LightGUI_ok})
  AC_MSG_RESULT(for full GUI: ${FullGUI_ok})
fi

AC_SUBST(GUI_LDFLAGS)
AC_SUBST(GUI_CXXFLAGS)
AC_SUBST(GUI_ROOT_DIR)
 
])dnl

AC_DEFUN([CHECK_SALOME_GUI],[
  CHECK_GUI_MODULE()
  SalomeGUI_ok=${LightGUI_ok}
])dnl

AC_DEFUN([CHECK_CORBA_IN_GUI],[
  CHECK_GUI_MODULE()
  CORBA_IN_GUI=${FullGUI_ok}
  AC_SUBST(CORBA_IN_GUI)
])dnl
