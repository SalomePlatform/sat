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

#  SuperVisionTest AddComponent : example of component that adds two numbers
#  File   : Makefile.in
#  Author : , CEA
#  Modified by : Alexander BORODIN (OCN) - autotools usage
#
include $(top_srcdir)/adm_local/unix/make_common_starter.am

# header files
salomeinclude_HEADERS = :sat:{CPPCMP}.hxx

# Libraries targets
lib_LTLIBRARIES = lib:sat:{CPPCMP}Engine.la
dist_lib:sat:{CPPCMP}Engine_la_SOURCES = \
	:sat:{CPPCMP}.cxx

lib:sat:{CPPCMP}Engine_la_CPPFLAGS = \
	$(CORBA_CXXFLAGS) \
	$(CORBA_INCLUDES) \
	$(KERNEL_CXXFLAGS) \
	-I$(top_builddir)/idl \
	-I$(top_builddir)

lib:sat:{CPPCMP}Engine_la_LDFLAGS = \
	../../idl/libSalomeIDL:sat:{CPPCMP}.la \
	$(KERNEL_LDFLAGS) \
	-lSalomeContainer \
	-lOpUtil \
	-lSalomeIDLKernel
