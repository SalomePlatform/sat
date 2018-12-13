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

# ---
# File   : :sat:{PYCMP}_utils.py
# Author : Vadim SANDLER, Open CASCADE S.A.S. (vadim.sandler@opencascade.com)
# ---
#
__all__ = [
    "moduleID",
    "objectID",
    "unknownID",
    "moduleName",
    "modulePixmap",
    "verbose",
    "getORB",
    "getNS",
    "getLCC",
    "getStudyManager",
    "getEngine",
    "getEngineIOR",
    "findOrCreateComponent",
    "getObjectID",
    ]

from omniORB import CORBA
from SALOME_NamingServicePy import SALOME_NamingServicePy_i
from LifeCycleCORBA import LifeCycleCORBA
import SALOMEDS
import SALOMEDS_Attributes_idl
import :sat:{PYCMP}_ORB

###
# Get :sat:{PYCMP} module's ID
###
def moduleID():
    MODULE_ID = 1000
    return MODULE_ID

###
# Get :sat:{PYCMP} object's ID
###
def objectID():
    OBJECT_ID = 1010
    return OBJECT_ID

###
# Get unknown ID
###
def unknownID():
    FOREIGN_ID = -1
    return FOREIGN_ID

###
# Get :sat:{PYCMP} module's name
###
def moduleName():
    return ":sat:{PYCMP}"

###
# Get module's pixmap name
###
def modulePixmap():
    return ":sat:{PYCMP}_small.png"

###
# Get verbose level
###
__verbose__ = None
def verbose():
    global __verbose__
    if __verbose__ is None:
        try:
            __verbose__ = int( os.getenv( 'SALOME_VERBOSE', 0 ) )
        except:
            __verbose__ = 0
            pass
        pass
    return __verbose__

###
# Get ORB reference
###
__orb__ = None
def getORB():
    global __orb__
    if __orb__ is None:
        __orb__ = CORBA.ORB_init( [''], CORBA.ORB_ID )
        pass
    return __orb__

###
# Get naming service instance
###
__naming_service__ = None
def getNS():
    global __naming_service__
    if __naming_service__ is None:
        __naming_service__ = SALOME_NamingServicePy_i( getORB() )
        pass
    return __naming_service__

##
# Get life cycle CORBA instance
##
__lcc__ = None
def getLCC():
    global __lcc__
    if __lcc__ is None:
        __lcc__ = LifeCycleCORBA( getORB() )
        pass
    return __lcc__

##
# Get study manager
###
__study_manager__ = None
def getStudyManager():
    global __study_manager__
    if __study_manager__ is None:
        obj = getNS().Resolve( '/myStudyManager' )
        __study_manager__ = obj._narrow( SALOMEDS.StudyManager )
        pass
    return __study_manager__

###
# Get :sat:{PYCMP} engine
###
__engine__ = None
def getEngine():
    global __engine__
    if __engine__ is None:
        __engine__ = getLCC().FindOrLoadComponent( "FactoryServerPy", moduleName() )
        pass
    return __engine__

###
# Get :sat:{PYCMP} engine IOR
###
def getEngineIOR():
    IOR = ""
    if getORB() and getEngine():
        IOR = getORB().object_to_string( getEngine() )
        pass
    return IOR

###
# Find or create :sat:{PYCMP} component object in a study
###
def findOrCreateComponent( study ):
    father = study.FindComponent( moduleName() )
    if father is None:
        builder = study.NewBuilder()
        father = builder.NewComponent( moduleName() )
        attr = builder.FindOrCreateAttribute( father, "AttributeName" )
        attr.SetValue( moduleName() )
        attr = builder.FindOrCreateAttribute( father, "AttributePixMap" )
        attr.SetPixMap( modulePixmap() )
        attr = builder.FindOrCreateAttribute( father, "AttributeLocalID" )
        attr.SetValue( moduleID() )
        try:
            builder.DefineComponentInstance( father, getEngine() )
            pass
        except:
            pass
        pass
    return father

###
# Get object's ID
###
def getObjectID( study, entry ):
    ID = unknownID()
    if study and entry:
        sobj = study.FindObjectID( entry )
        if sobj is not None:
            test, anAttr = sobj.FindAttribute( "AttributeLocalID" )
            if test: ID = anAttr._narrow( SALOMEDS.AttributeLocalID ).Value()
            pass
        pass
    return ID
