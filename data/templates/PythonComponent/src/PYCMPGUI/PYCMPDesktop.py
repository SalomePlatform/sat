from qtsalome import *
from TreeWidget import TreeWidget
from GraphicsView import GraphicsView
from GraphicsScene import GraphicsScene

class :sat:{PYCMP}Desktop( QMainWindow ) :

   def __init__( self, sgPyQt, sg  ) :
       """Constructor"""

       QMainWindow.__init__( self )
       self._controller = None
       self._sgPyQt = sgPyQt
       self._sg = sg
       self._sgDesktop = self._sgPyQt.getDesktop()

       # Menus IDs
       self._curveMenuID = 1000
       self._advancedMenuID = 1001

       # Actions IDs
       self._polylineID = 1002
       self._circleID = 1003
       self._deleteAllID = 1004

       self.createTreeView()
       self.createGraphicsView()
       pass

   def createTreeView( self ) :
       self._globalTree= TreeWidget( self )
       self._globalTree.setHeaderLabel ( "Tree view" )
       self._dockGlobalTree = QDockWidget( self._sgDesktop )
       self._dockGlobalTree.setFeatures( QDockWidget.NoDockWidgetFeatures )
       self._dockGlobalTree.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       self._dockGlobalTree.setWidget( self._globalTree )
       self._sgDesktop.addDockWidget( Qt.LeftDockWidgetArea, self._dockGlobalTree )
       pass

   def createGraphicsView( self ) :
       scene = GraphicsScene( self._controller )
       self._globalGraphicsView = GraphicsView( scene )
       self._globalGraphicsViewID = self._sgPyQt.createView( "ViewCurve", self._globalGraphicsView )
       pass

   def createActions( self ) :
       self.createPolylineAction = self._sgPyQt.createAction( self._polylineID, "Polyline", "Create Polyline", "Show Polyline dialog box", "ExecPolyline.png" )
       self.createCircleAction = self._sgPyQt.createAction( self._circleID, "Circle", "Create Circle", "Show Circle dialog box", "ExecCircle.png" )
       self.deleteAllAction = self._sgPyQt.createAction( self._deleteAllID, "Delete all", "Delete all", "Delete all objects", "ExecDelAll.png" )
       pass

   def createMenus( self ) :
       curveMenu = self._sgPyQt.createMenu( " Curve", -1, self._curveMenuID, self._sgPyQt.defaultMenuGroup() )
       advancedMenu = self._sgPyQt.createMenu( " Advanced", -1, self._advancedMenuID, self._sgPyQt.defaultMenuGroup() )

       self._sgPyQt.createMenu( self.createPolylineAction, curveMenu )
       self._sgPyQt.createMenu( self.createCircleAction, curveMenu )
       self._sgPyQt.createMenu( self.deleteAllAction, advancedMenu )
       pass

   def createToolBars( self ) :
       createPolylineTB = self._sgPyQt.createTool("New polyline")
       createCircleTB = self._sgPyQt.createTool("New circle")
       deleteAllTB = self._sgPyQt.createTool("Delete all")

       self._sgPyQt.createTool( self.createPolylineAction, createPolylineTB )
       self._sgPyQt.createTool( self.createCircleAction, createCircleTB )
       self._sgPyQt.createTool( self.deleteAllAction, deleteAllTB )
       pass

   def createPopups( self ) :
       pass

   def getController( self ) :
       return self._controller

   def setController( self, controller ) :
       self._controller = controller
       pass

   def getGlobalTree( self ) :
       return self._globalTree

   def getGlobalGraphicsView( self ) :
       return self._globalGraphicsView

   def getGlobalGraphicsViewID( self ) :
       return self._globalGraphicsViewID

   def getDockGlobalTree( self ) :
       return self._dockGlobalTree

   def updateGlobalGraphicsView( self, scene ) :
       self._globalGraphicsView.setScene( scene )
       if scene is None : return
       #Resizing the globalGraphicView
       sceneRect = scene.getRect()
       self._globalGraphicsView.fitInView ( sceneRect, Qt.KeepAspectRatio )
       pass

pass
