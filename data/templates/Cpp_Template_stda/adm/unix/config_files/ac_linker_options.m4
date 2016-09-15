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

dnl @synopsis AC_LINKER_OPTIONS
dnl Check warning flags for C++ compiler to control warning messages
dnl
AC_DEFUN([AC_LINKER_OPTIONS],[

  AC_CHECKING(for LIB_LOCATION_SUFFIX)
  LIB_LOCATION_SUFFIX=""
  AC_SUBST(LIB_LOCATION_SUFFIX)
  AC_MSG_RESULT(LIB_LOCATION_SUFFIX is $LIB_LOCATION_SUFFIX)

  for opt in "-Xlinker -export-dynamic" -transitive_link; do
    AC_CXX_OPTION($opt,LDEXPDYNFLAGS,flag=yes,flag=no)
    if test "$flag" = "yes"; then
      break
    fi
  done
  AC_SUBST(LDEXPDYNFLAGS)

  for opt in "-Xlinker -enable-new-dtags" ; do
    AC_CXX_OPTION($opt,LDFLAGS)
  done
  AC_SUBST(LDFLAGS)

dnl 
  case $host_os in
    osf*)
      STDLIB="-lcxxstd"
      ;;
    *)
      STDLIB="-lstdc++"
      ;;
  esac
  AC_SUBST(STDLIB)
])
