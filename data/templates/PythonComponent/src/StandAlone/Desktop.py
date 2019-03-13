from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from TreeWidget import TreeWidget
from GraphicsView import GraphicsView
from GraphicsScene import GraphicsScene

class Desktop( QMainWindow ) :

   def __init__( self ) :
       """Constructor"""

       QMainWindow.__init__( self )
       self._controller = None

       # Creating a dockWidget which will contain globalTree
       self._globalTree= TreeWidget( self )
       self._globalTree.setHeaderLabel ( "Object browser" )
       dockGlobalTree = QDockWidget( "Tree view", self )
       dockGlobalTree.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       dockGlobalTree.setWidget( self._globalTree )
       self.addDockWidget( Qt.LeftDockWidgetArea, dockGlobalTree )

       # Creating a central widget which contains the globalGraphicsView
       self._dockGlobalView = QDockWidget( "Graphics view", self )
       scene = GraphicsScene( self._controller )
       self._globalGraphicsView = GraphicsView( scene )
       self._dockGlobalView.setWidget( self._globalGraphicsView )
       self._globalGraphicsView.show()
       self.setCentralWidget( self._dockGlobalView )

       # Creating menus and toolbars
       self.createMenus()
       self.createToolBars()
       pass

   def getController( self ) :
       return self._controller

   def setController( self, controller ) :
       self._controller = controller
       pass

   def getGlobalTree( self ) :
       return self._globalTree

   def createMenus( self ) :
       # Creating menus
       curveMenu = self.menuBar().addMenu( "Curve" )
       toolsMenu = self.menuBar().addMenu( "Tools" )
       # Adding actions
       createPolylineAction = QAction( "Polyline", self )
       createCircleAction = QAction( "Circle", self )
       curveMenu.addAction( createPolylineAction )
       curveMenu.addAction( createCircleAction )

       deleteAllAction = QAction( "Delete all", self )
       toolsMenu.addAction( deleteAllAction )
       # Connecting slots
       createPolylineAction.triggered.connect(self.showCreatePolylineDialog)
       createCircleAction.triggered.connect(self.showCreateCircleDialog)
       deleteAllAction.triggered.connect(self.deleteAll)
       pass

   def createToolBars( self ) :
       # Creating toolBars
       createPolylineTB = self.addToolBar( "New polyline")
       createCircleTB = self.addToolBar( "New circle")
       createPolylineAction = QAction( "Polyline", self )
       createCircleAction = QAction( "Circle", self )
       # Adding actions
       createPolylineTB.addAction( createPolylineAction )
       createCircleTB.addAction( createCircleAction )
       # Connecting slots
       createPolylineAction.triggered.connect(self.showCreatePolylineDialog)
       createCircleAction.triggered.connect(self.showCreateCircleDialog)
       pass

   def showCreatePolylineDialog( self ) :
       from CreatePolylineDialog import CreatePolylineDialog

       widgetDialogBox = QDockWidget( "myDockWidget", self )
       myDialog = CreatePolylineDialog( "www.google.fr", self._controller, widgetDialogBox )
       widgetDialogBox.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       widgetDialogBox.setWidget( myDialog )
       widgetDialogBox.setWindowTitle( "Polyline definition" )
       self.addDockWidget( Qt.LeftDockWidgetArea, widgetDialogBox )
       pass

   def showCreateCircleDialog( self ) :
       from CreateCircleDialog import CreateCircleDialog

       widgetDialogBox = QDockWidget( "myDockWidget", self )
       myDialog = CreateCircleDialog( "www.cea.fr", self._controller, widgetDialogBox )
       widgetDialogBox.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       widgetDialogBox.setWidget( myDialog )
       widgetDialogBox.setWindowTitle( "Polyline definition" )
       self.addDockWidget( Qt.LeftDockWidgetArea, widgetDialogBox )
       pass

   def deleteAll( self ) :
       models = self.getController().getModels()
       if len( models ) == 0 : return
       answer = QMessageBox.question( self, 'Confirmation', 'Do you really want to delete all the existing objects ?' , QMessageBox.Yes | QMessageBox.No )
       if answer == QMessageBox.Yes :
          for model in models :
             self.getController().removeModel( model )
             pass
          pass
       pass

   def updateGlobalGraphicsView( self, scene ) :
       self._globalGraphicsView.setScene( scene )
       if scene is None :
          self._dockGlobalView.setWindowTitle( "Graphics view" )
          return
       self._dockGlobalView.setWindowTitle( "Graphics view : showing " + scene.getModel().getName() )
       #Resizing the globalGraphicView
       sceneRect = scene.getRect()
       topLeft = sceneRect.topLeft()
       viewRect = QRectF( topLeft.x(), topLeft.y(), 2*sceneRect.width(), 2*sceneRect.height() )
       self._globalGraphicsView.fitInView ( viewRect, Qt.IgnoreAspectRatio )
       pass

pass
