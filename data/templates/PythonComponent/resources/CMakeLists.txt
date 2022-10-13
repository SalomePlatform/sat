# Copyright (C) 2018-2018  CEA/DEN
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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

SET(Others_RESOURCES
	:sat:{PYCMP}.png
	:sat:{PYCMP}_small.png
	Exec:sat:{PYCMP}.png
	handshake.png
	stop.png
	ExecDelAll.png
	ExecCircle.png
	ExecPolyline.png
	SalomeApp.xml
	:sat:{PYCMP}Catalog.xml
)

INSTALL(FILES ${Others_RESOURCES} DESTINATION ${SALOME_:sat:{PYCMP}_INSTALL_RES_DATA})
INSTALL(FILES SalomeApp.xml RENAME SalomeAppSL.xml DESTINATION ${SALOME_:sat:{PYCMP}_INSTALL_RES_DATA})
