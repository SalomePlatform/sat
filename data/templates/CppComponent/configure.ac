# Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

#  PLEASE DO NOT MODIFY configure.in FILE
#  ALL CHANGES WILL BE DISCARDED BY THE NEXT
#  build_configure COMMAND
#  CHANGES MUST BE MADE IN configure.in.base FILE
# Author : Marc Tajchman (CEA)
# Date : 28/06/2001
# Modified by : Patrick GOLDBRONN (CEA)
# Modified by : Marc Tajchman (CEA)
# Created from configure.in.base
#
AC_INIT([Salome2 Project :sat:{CPPCMP} module],[6.6.0], [webmaster.salome@opencascade.com], [Salome:sat:{CPPCMP}])
AC_CONFIG_AUX_DIR(adm_local/unix/config_files)
AC_CANONICAL_HOST
AC_CANONICAL_TARGET
AM_INIT_AUTOMAKE([-Wno-portability])

XVERSION=`echo $VERSION | awk -F. '{printf("0x%02x%02x%02x",$1,$2,$3)}'`
AC_SUBST(XVERSION)
VERSION_DEV=0
AC_SUBST(VERSION_DEV)

# set up MODULE_NAME variable for dynamic construction of directories (resources, etc.)
MODULE_NAME=:sat:{CPPCMP_minus}
AC_SUBST(MODULE_NAME)

dnl
dnl Initialize source and build root directories
dnl

ROOT_BUILDDIR=`pwd`
ROOT_SRCDIR=`echo $0 | sed -e "s,[[^/]]*$,,;s,/$,,;s,^$,.,"`
cd $ROOT_SRCDIR
ROOT_SRCDIR=`pwd`
cd $ROOT_BUILDDIR

AC_SUBST(ROOT_SRCDIR)
AC_SUBST(ROOT_BUILDDIR)

echo
echo Source root directory : $ROOT_SRCDIR
echo Build  root directory : $ROOT_BUILDDIR
echo
echo

AC_CHECK_PROG(SHELL,sh)
AC_SUBST(SHELL)

if test -z "$AR"; then
   AC_CHECK_PROGS(AR,ar xar,:,$PATH)
fi
AC_SUBST(AR)

dnl Export the AR macro so that it will be placed in the libtool file
dnl correctly.
export AR

echo
echo ---------------------------------------------
echo testing make
echo ---------------------------------------------
echo

AC_PROG_MAKE_SET
AC_PROG_INSTALL
AC_LOCAL_INSTALL
dnl
dnl libtool macro check for CC, LD, NM, LN_S, RANLIB, STRIP + for shared libraries

AC_ENABLE_DEBUG(yes)
AC_DISABLE_PRODUCTION

echo ---------------------------------------------
echo testing libtool
echo ---------------------------------------------

dnl first, we set static to no!
dnl if we want it, use --enable-static
AC_ENABLE_STATIC(no)

AC_LIBTOOL_DLOPEN
AC_PROG_LIBTOOL

dnl Fix up the INSTALL macro if it s a relative path. We want the
dnl full-path to the binary instead.
case "$INSTALL" in
   *install-sh*)
      INSTALL='\${KERNEL_ROOT_DIR}'/adm_local/unix/config_files/install-sh
      ;;
esac

echo
echo ---------------------------------------------
echo testing C/C++
echo ---------------------------------------------
echo

cc_ok=no
dnl inutil car libtool
dnl AC_PROG_CC
AC_PROG_CXX
AC_CXX_WARNINGS
AC_CXX_TEMPLATE_OPTIONS
AC_DEPEND_FLAG
# AC_CC_WARNINGS([ansi])
cc_ok=yes

dnl Library libdl :
AC_CHECK_LIB(dl,dlopen)

dnl Library librt : for alpha/osf
AC_CHECK_LIB(rt,nanosleep)

dnl add library libm :
AC_CHECK_LIB(m,ceil)

AC_CXX_USE_STD_IOSTREAM
AC_CXX_HAVE_SSTREAM

dnl
dnl ---------------------------------------------
dnl testing linker
dnl ---------------------------------------------
dnl

AC_LINKER_OPTIONS

echo
echo ---------------------------------------------
echo testing threads
echo ---------------------------------------------
echo

ENABLE_PTHREADS

echo
echo ---------------------------------------------
echo testing python
echo ---------------------------------------------
echo

CHECK_PYTHON

AM_PATH_PYTHON(2.3)

echo
echo ---------------------------------------------
echo Testing GUI
echo ---------------------------------------------
echo

CHECK_GUI_MODULE

gui_ok=no
if test "${SalomeGUI_need}" != "no" -a "${FullGUI_ok}" = "yes" ; then
  gui_ok=yes
fi

AM_CONDITIONAL(:sat:{CPPCMP}_ENABLE_GUI, [test "${gui_ok}" = "yes"])

if test "${SalomeGUI_need}" == "yes"; then
  if test "${FullGUI_ok}" != "yes"; then
    AC_MSG_WARN(For configure :sat:{CPPCMP} module necessary full GUI!)
  fi
elif test "${SalomeGUI_need}" == "auto"; then
  if test "${FullGUI_ok}" != "yes"; then
    AC_MSG_WARN(Full GUI not found. Build will be done without GUI!)
  fi
elif test "${SalomeGUI_need}" == "no"; then
  echo Build without GUI option has been chosen
fi

if test "${gui_ok}" = "yes"; then
	echo
	echo ---------------------------------------------
	echo testing QT
	echo ---------------------------------------------
	echo

	CHECK_QT

fi

echo
echo ---------------------------------------------
echo testing MPI
echo ---------------------------------------------
echo

CHECK_MPI

echo
echo ---------------------------------------------
echo testing HDF5
echo ---------------------------------------------
echo

CHECK_HDF5

echo
echo ---------------------------------------------
echo BOOST Library
echo ---------------------------------------------
echo

CHECK_BOOST

echo
echo ---------------------------------------------
echo Testing OpenCascade
echo ---------------------------------------------
echo

CHECK_CAS

echo
echo ---------------------------------------------
echo testing omniORB
echo ---------------------------------------------
echo

CHECK_OMNIORB

echo
echo ---------------------------------------------
echo default ORB : omniORB
echo ---------------------------------------------
echo

DEFAULT_ORB=omniORB
CHECK_CORBA

AC_SUBST_FILE(CORBA)
corba=make_$ORB
CORBA=adm_local/unix/$corba

echo
echo ---------------------------------------------
echo Testing html generators
echo ---------------------------------------------
echo

CHECK_HTML_GENERATORS

echo
echo ---------------------------------------------
echo Testing Kernel
echo ---------------------------------------------
echo

CHECK_KERNEL

echo
echo ---------------------------------------------
echo Summary
echo ---------------------------------------------
echo

echo Configure

if test "${gui_ok}" = "yes"; then
  variables="cc_ok threads_ok boost_ok python_ok omniORB_ok qt_ok hdf5_ok doxygen_ok Kernel_ok gui_ok"
elif test "${SalomeGUI_need}" != "no"; then
  variables="cc_ok threads_ok boost_ok python_ok omniORB_ok hdf5_ok doxygen_ok Kernel_ok gui_ok"
else
  variables="cc_ok threads_ok boost_ok python_ok omniORB_ok hdf5_ok doxygen_ok Kernel_ok"
fi

for var in $variables
do
   printf "   %10s : " `echo \$var | sed -e "s,_ok,,"`
   eval echo \$$var
done

echo
echo "Default ORB   : $DEFAULT_ORB"
echo

dnl We don t need to say when we re entering directories if we re using
dnl GNU make becuase make does it for us.
if test "X$GMAKE" = "Xyes"; then
   AC_SUBST(SETX) SETX=":"
else
   AC_SUBST(SETX) SETX="set -x"
fi
echo
echo ---------------------------------------------
echo generating Makefiles and configure files
echo ---------------------------------------------
echo

AC_OUTPUT_COMMANDS([ \
      chmod +x ./bin/*; \
])

AC_HACK_LIBTOOL
AC_CONFIG_COMMANDS([hack_libtool],[
sed -i "s%^CC=\"\(.*\)\"%hack_libtool (){ \n\
  $(pwd)/hack_libtool \1 \"\$[@]\" \n\
}\n\
CC=\"hack_libtool\"%g" libtool
sed -i "s%\(\s*\)for searchdir in \$newlib_search_path \$lib_search_path \$sys_lib_search_path \$shlib_search_path; do%\1searchdirs=\"\$newlib_search_path \$lib_search_path \$sys_lib_search_path \$shlib_search_path\"\n\1for searchdir in \$searchdirs; do%g" libtool
sed -i "s%\(\s*\)searchdirs=\"\$newlib_search_path \$lib_search_path \(.*\)\"%\1searchdirs=\"\$newlib_search_path \$lib_search_path\"\n\1sss_beg=\"\"\n\1sss_end=\"\2\"%g" libtool
sed -i "s%\(\s*\)\(for searchdir in \$searchdirs; do\)%\1for sss in \$searchdirs; do\n\1  if ! test -d \$sss; then continue; fi\n\1  ssss=\$(cd \$sss; pwd)\n\1  if test \"\$ssss\" != \"\" \&\& test -d \$ssss; then\n\1    case \$ssss in\n\1      /usr/lib | /usr/lib64 ) ;;\n\1      * ) sss_beg=\"\$sss_beg \$ssss\" ;;\n\1    esac\n\1  fi\n\1done\n\1searchdirs=\"\$sss_beg \$sss_end\"\n\1\2%g" libtool
],[])

# This list is initiated using autoscan and must be updated manually
# when adding a new file <filename>.in to manage. When you execute
# autoscan, the Makefile list is generated in the output file configure.scan.
# This could be helpfull to update de configuration.
AC_OUTPUT([ \
  adm_local/Makefile \
  adm_local/unix/Makefile \
  adm_local/unix/config_files/Makefile \
  bin/VERSION \
  bin/runAppli \
  bin/Makefile \
  doc/Makefile \
  doc/doxyfile \
  doc/static/header.html \
  :sat:{CPPCMP}_version.h \
  resources/:sat:{CPPCMP}Catalog.xml \
  resources/SalomeApp.xml \
  src/Makefile \
  src/:sat:{CPPCMP}/Makefile \
  src/:sat:{CPPCMP}GUI/Makefile \
  resources/Makefile \
  idl/Makefile \
  Makefile \
])
