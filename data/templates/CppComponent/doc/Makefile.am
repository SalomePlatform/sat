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

include $(top_srcdir)/adm_local/unix/make_common_starter.am

EXTRA_DIST += images static/footer.html static/doxygen.css

guidocdir = $(docdir)/gui/:sat:{CPPCMP}
guidoc_DATA = images/head.png

usr_docs: doxyfile
	$(DOXYGEN) doxyfile

docs: usr_docs

dev_docs:

clean-local:
	@for filen in `find . -maxdepth 1` ; do			\
	  case $${filen} in					\
	    ./Makefile | ./doxyfile ) ;;			\
	    . | .. | ./static) ;;				\
	    *) echo "Removing $${filen}" ; rm -rf $${filen} ;;	\
	  esac ;						\
	done ;

install-data-local: usr_docs
	$(INSTALL) -d $(DESTDIR)$(docdir)/gui/:sat:{CPPCMP}
	@for filen in `find . -maxdepth 1` ; do			\
	  case $${filen} in					\
	    ./Makefile | ./doxyfile | ./doxyfile.bak ) ;;	\
	    . | .. | ./static ) ;;				\
	    *) echo "Installing $${filen}" ; cp -rp $${filen} $(DESTDIR)$(docdir)/gui/:sat:{CPPCMP} ;;	\
	  esac ;										\
	done ;

uninstall-local:
	rm -rf $(DESTDIR)$(docdir)/gui/:sat:{CPPCMP}
