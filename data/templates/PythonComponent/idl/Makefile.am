#  Copyright (C) 2007-2010  CEA/DEN, EDF R&D, OPEN CASCADE
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#  See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

# This Makefile is responsible of generating the client and server
# implementation of IDL interfaces for both C++ and python usage.
# The building process of the C++ files is in charge of each source
# package and then is not manage here.
#
include $(top_srcdir)/adm_local/unix/make_common_starter.am

BASEIDL_FILES = :sat:{PYCMP}_Gen.idl

# This variable defines the files to be installed
dist_salomeidl_DATA = $(BASEIDL_FILES)

# These variables defines the building process of CORBA files
OMNIORB_IDL         = @OMNIORB_IDL@
OMNIORB_IDLCXXFLAGS = @OMNIORB_IDLCXXFLAGS@
OMNIORB_IDLPYFLAGS  = \
	@OMNIORB_IDLPYFLAGS@ \
	-I$(top_builddir)/idl/salome \
	-I$(KERNEL_ROOT_DIR)/idl/salome

IDLCXXFLAGS = \
	-bcxx \
	@IDLCXXFLAGS@ \
	-I$(top_builddir)/idl/salome \
	-I$(KERNEL_ROOT_DIR)/idl/salome
IDLPYFLAGS  = \
	@IDLPYFLAGS@ \
	-I$(KERNEL_ROOT_DIR)/idl/salome

install-exec-local: $(BASEIDL_FILES:%=$(top_srcdir)/idl/%)
	$(INSTALL) -d  $(DESTDIR)$(salomepythondir)
	@for file in $^ dummy; do \
          if [ $$file != "dummy" ]; then \
             $(OMNIORB_IDL) $(OMNIORB_IDLPYFLAGS) -C$(DESTDIR)$(salomepythondir) $$file ; \
          fi ; \
        done ;

# uninstall-local removes too much, but it works in distcheck
uninstall-local:
	rm -rf $(DESTDIR)$(salomepythondir)/*

mostlyclean-local:
	-rm -f *.py

