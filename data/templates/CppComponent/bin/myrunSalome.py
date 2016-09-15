#!/usr/bin/env python
# Copyright (C) 2007-2012  CEA/DEN, EDF R&D, OPEN CASCADE
#
# Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
# CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
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

def test(clt):
   """
        Test function that creates an instance of :sat:{CPPCMP} component
        usage : comp = test(clt)
   """
   # create an LifeCycleCORBA instance
   import LifeCycleCORBA
   lcc = LifeCycleCORBA.LifeCycleCORBA(clt.orb)
   import :sat:{CPPCMP}_ORB
   comp = lcc.FindOrLoadComponent("FactoryServer", ":sat:{CPPCMP}")
   return comp

#

if __name__ == "__main__":
   import user
   from runSalome import *
   clt,args = main()

   #
   #  Impression arborescence Naming Service
   #

   if clt != None:
     print
     print " --- registered objects tree in Naming Service ---"
     clt.showNS()
     session=clt.waitNS("/Kernel/Session")
     catalog=clt.waitNS("/Kernel/ModulCatalog")
     import socket
     container =  clt.waitNS("/Containers/" + socket.gethostname().split('.')[0] + "/FactoryServer")
