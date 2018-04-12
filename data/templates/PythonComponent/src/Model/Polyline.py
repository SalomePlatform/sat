from Model import *
from qtsalome import *

class Polyline( Model ):

   def __init__( self, name, points, controller ):
       """Constructor"""

       Model.__init__( self, controller )
       self._name = name
       self._points = points
       self.addTreeWidgetItem( self.getName(), controller )
       self.addGraphicScene( controller )
       pass

   def getPoints( self ):
       return self._points

   def setPoints( self, points ):
       self._points = points
       pass

   def editPoint( self, pointRange, newPoint ) :
       self._points[ pointRange ] = newPoint
       pass

   def addTreeWidgetItem( self, name, controller ):
       from PolyTreeWidgetItem import PolyTreeWidgetItem
       from TreeWidgetItem import TreeWidgetItem

       myTreeWidgetItem = PolyTreeWidgetItem( name, controller, ["Show", "Rename", "Delete"] )
       # Adding list of points
       for point in self.getPoints() :
          x = point[0]
          y = point[1]
          newTreeWidgetItem = TreeWidgetItem( str(x) + ":" + str(y), controller, ["Edit"] )
          myTreeWidgetItem.addChild( newTreeWidgetItem )
          pass
       myTreeWidgetItem.setModel( self )
       self.getViews().append( myTreeWidgetItem )
       return myTreeWidgetItem

   def addGraphicScene( self, controller ) :
       from PolyGraphicsScene import PolyGraphicsScene

       myGraphicsScene = PolyGraphicsScene( controller )
       myGraphicsScene.setModel( self )
       self.getViews().append( myGraphicsScene )
       return myGraphicsScene

   def save( self ):
       pass

pass
