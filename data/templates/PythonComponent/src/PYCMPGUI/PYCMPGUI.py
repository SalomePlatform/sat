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
# File   : :sat:{PYCMP}GUI.py
# Author : Vadim SANDLER, Open CASCADE S.A.S. (vadim.sandler@opencascade.com)
# ---
#
import traceback
import string
import os
import sys
from qtsalome import *

#from :sat:{PYCMP}_utils import *

import salome
from Controller import Controller
from TreeWidget import TreeWidget
from :sat:{PYCMP}Desktop import :sat:{PYCMP}Desktop

# Get SALOME PyQt interface
import SalomePyQt
import libSALOME_Swig

########################################################
# Global variables
########################################################

sgPyQt = SalomePyQt.SalomePyQt()
sg = libSALOME_Swig.SALOMEGUI_Swig()
sgDesktop = sgPyQt.getDesktop()
widgetDialogBox = None

objectsManager = Controller( None )
moduleDesktop   = {}
currentDesktop = None

CURVE_MENU_ID = 1000
ADVANCED_MENU_ID = 1001
POLYLINE_ID = 1002
CIRCLE_ID = 1003
DEL_ALL_ID = 1004

########################################################
# Internal methods
########################################################

def getStudyId():
    """This method returns the active study ID"""
    return sgPyQt.getStudyId()

def getStudy():
    """This method returns the active study"""

    studyId = _getStudyId()
    study = getStudyManager().GetStudyByID( studyId )
    return study

def getDesktop():
    """This method returns the current :sat:{PYCMP} desktop"""

    global currentDesktop
    return currentDesktop

def setDesktop( studyID ):
    """This method sets and returns :sat:{PYCMP} desktop"""

    global moduleDesktop, currentDesktop, objectsManager

    if not studyID in moduleDesktop:
        moduleDesktop[studyID] = :sat:{PYCMP}Desktop( sgPyQt, sg )
        objectsManager = Controller( moduleDesktop[studyID] )
        moduleDesktop[studyID].setController( objectsManager )
        pass
    currentDesktop = moduleDesktop[studyID]
    return currentDesktop

def incObjToMap( m, id ):
    """This method incrementes the object counter in the map"""

    if id not in m: m[id] = 0
    m[id] += 1
    pass

def getSelection():
    """This method analyses selection"""

    selcount = sg.SelectedCount()
    seltypes = {}
    for i in range( selcount ):
        incObjToMap( seltypes, getObjectID( getStudy(), sg.getSelected( i ) ) )
        pass
    return selcount, seltypes

################################################
# Callback functions
################################################

def initialize():
    """This method is called when module is initialized. It performs initialization actions"""

    setDesktop( getStudyId() )
    pass

def windows():
    """This method is called when module is initialized. It returns a map of popup windows to be used by the module"""

    wm = {}
    wm[SalomePyQt.WT_ObjectBrowser] = Qt.LeftDockWidgetArea
    wm[SalomePyQt.WT_PyConsole]     = Qt.BottomDockWidgetArea
    return wm

def views():
    """This method is called when module is initialized. It returns a list of 2D/3D views to be used by the module"""
    return []

def createPreferences():
    """This method is called when module is initialized. It exports module preferences"""
    pass

def activate():
    """This method is called when module is initialized. It returns True if activating is successfull, False otherwise"""

    global moduleDesktop, sgPyQt, widgetDialogBox

    widgetDialogBox = QDockWidget( sgDesktop )
    moduleDesktop[getStudyId()].createActions()
    moduleDesktop[getStudyId()].createMenus()
    moduleDesktop[getStudyId()].createToolBars()
    moduleDesktop[getStudyId()].createPopups()
    moduleDesktop[getStudyId()].getDockGlobalTree().show()
    moduleDesktop[getStudyId()].getGlobalGraphicsView().show()
    sgPyQt.activateView( moduleDesktop[getStudyId()].getGlobalGraphicsViewID() )
    return True

def viewTryClose( wid ):
    sgPyQt.setViewClosable(wid, True)
    pass

def deactivate():
    """This method is called when module is deactivated"""

    global moduleDesktop, widgetDialogBox

    widgetDialogBox.close()
    moduleDesktop[getStudyId()].getDockGlobalTree().hide()
    moduleDesktop[getStudyId()].updateGlobalGraphicsView( None )
    moduleDesktop[getStudyId()].getGlobalGraphicsView().hide()
    pass

def activeStudyChanged( studyID ):
    """This method is called when active study is changed"""

    setDesktop( getStudyId() )
    pass

def createPopupMenu( popup, context ):
    """This method is called when popup menu is invocked"""
    pass

def OnGUIEvent( commandID ):
    """This method is called when a GUI action is activated"""

    if commandID in dict_command:
       dict_command[commandID]()
       pass
    pass

def preferenceChanged( section, setting ):
    """This method is called when module's preferences are changed"""
    pass

def activeViewChanged( viewID ):
    """This method is called when active view is changed"""
    pass

def viewCloned( viewID ):
    """This method is called when active view is cloned"""
    pass

def viewClosed( viewID ):
    """This method is called when active view viewClosed"""
    pass

def engineIOR():
    """This method is called when study is opened. It returns engine IOR"""
    return getEngineIOR()


################################################
# GUI actions implementation
################################################

def showCreatePolylineDialog() :
    from CreatePolylineDialog import CreatePolylineDialog

    global widgetDialogBox
    widgetDialogBox = QDockWidget( sgDesktop )
    myDialog = CreatePolylineDialog( "www.cea.fr", objectsManager, widgetDialogBox )
    widgetDialogBox.setWidget( myDialog )
    widgetDialogBox.setWindowTitle( "Polyline definition" )
    sgDesktop.addDockWidget(Qt.LeftDockWidgetArea, widgetDialogBox)
    pass

def showCreateCircleDialog() :
    from CreateCircleDialog import CreateCircleDialog

    global widgetDialogBox
    widgetDialogBox = QDockWidget( sgDesktop )
    myDialog = CreateCircleDialog( "www.cea.fr", objectsManager, widgetDialogBox )
    widgetDialogBox.setWidget( myDialog )
    widgetDialogBox.setWindowTitle( "Circle definition" )
    sgDesktop.addDockWidget(Qt.LeftDockWidgetArea, widgetDialogBox)
    pass

def deleteAll() :
    models = moduleDesktop[getStudyId()].getController().getModels()
    if len( models ) == 0 : return
    answer = QMessageBox.question( moduleDesktop[getStudyId()], 'Confirmation', 'Do you really want to delete all the existing objects ?' , QMessageBox.Yes | QMessageBox.No )
    if answer == QMessageBox.Yes :
       for model in models :
          moduleDesktop[getStudyId()].getController().removeModel( model )
          pass
       pass
    pass

########################################################
# Commands dictionary
########################################################

dict_command = { POLYLINE_ID : showCreatePolylineDialog,
                 CIRCLE_ID   : showCreateCircleDialog,
                 DEL_ALL_ID : deleteAll
                }

########################################################
