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

dnl @synopsis AC_CXX_OPTION(-option,variable where we add option if ok,action if ok; action if not ok)
dnl Check options for C++ compiler
dnl @author Bernard Secher - 15/01/2004
dnl
AC_DEFUN([AC_CXX_OPTION], [
  AC_MSG_CHECKING(wether $CXX accepts $1)
  cat > conftest.cxx <<EOF
int main() { return 0; }
EOF
  $CXX $1 conftest.cxx > conftest.log 2>&1
  var=`echo $1 | sed -e "s, .*$,," | sed -e "s,^-,,"`
#CCRT  if ! grep -e $var conftest.log > /dev/null 2>&1 ; then
  if grep -e $var conftest.log > /dev/null 2>&1 ; then
    AC_MSG_RESULT(no)
    eval $4
  else
    AC_MSG_RESULT(yes)
    $2="${$2} $1"
    eval $3
  fi
])


