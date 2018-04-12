#  Copyright (C) 2007-2010  CEA/DEN, EDF R&D, OPEN CASCADE
#
#  Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
#  CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
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

# ---
# File   : :sat:{PYCMP}.py
# Author : Vadim SANDLER, Open CASCADE S.A.S. (vadim.sandler@opencascade.com)
# ---
#
import :sat:{PYCMP}_ORB__POA
import SALOME_ComponentPy
import SALOME_DriverPy

from :sat:{PYCMP}_utils import *

class :sat:{PYCMP}(:sat:{PYCMP}_ORB__POA.:sat:{PYCMP}_Gen,
              SALOME_ComponentPy.SALOME_ComponentPy_i,
              SALOME_DriverPy.SALOME_DriverPy_i):
    """
    Construct an instance of :sat:{PYCMP} module engine.
    The class :sat:{PYCMP} implements CORBA interface :sat:{PYCMP}_Gen (see :sat:{PYCMP}_Gen.idl).
    It is inherited from the classes SALOME_ComponentPy_i (implementation of
    Engines::EngineComponent CORBA interface - SALOME component) and SALOME_DriverPy_i
    (implementation of SALOMEDS::Driver CORBA interface - SALOME module's engine).
    """
    def __init__ ( self, orb, poa, contID, containerName, instanceName,
                   interfaceName ):
        SALOME_ComponentPy.SALOME_ComponentPy_i.__init__(self, orb, poa,
                    contID, containerName, instanceName, interfaceName, 0)
        SALOME_DriverPy.SALOME_DriverPy_i.__init__(self, interfaceName)
        #
        self._naming_service = SALOME_ComponentPy.SALOME_NamingServicePy_i( self._orb )
        #
        pass

    """
    Touch the component
    """
    def touch(self, name):
        message = "Touch: %s!" % name
        return message

    """
    Create object.
    """
    def createObject( self, study, name ):
        builder = study.NewBuilder()
        father  = findOrCreateComponent( study )
        object  = builder.NewObject( father )
        attr    = builder.FindOrCreateAttribute( object, "AttributeName" )
        attr.SetValue( name )
        attr    = builder.FindOrCreateAttribute( object, "AttributeLocalID" )
        attr.SetValue( objectID() )
        pass

    """
    Dump module data to the Python script.
    """
    def DumpPython( self, study, isPublished ):
        abuffer = []
        abuffer.append( "def RebuildData( theStudy ):" )
        names = []
        father = study.FindComponent( moduleName() )
        if father:
            iter = study.NewChildIterator( father )
            while iter.More():
                name = iter.Value().GetName()
                if name: names.append( name )
                iter.Next()
                pass
            pass
        if names:
            abuffer += [ "  from batchmode_salome import lcc" ]
            abuffer += [ "  import :sat:{PYCMP}_ORB" ]
            abuffer += [ "  " ]
            abuffer += [ "  myCompo = lcc.FindOrLoadComponent( 'FactoryServerPy', '%s' )" % moduleName() ]
            abuffer += [ "  " ]
            abuffer += [ "  myCompo.createObject( theStudy, '%s' )" % name for name in names ]
            pass
        abuffer += [ "  " ]
        abuffer.append( "  pass" )
        abuffer.append( "\0" )
        return ("\n".join( abuffer ), 1)
