from Model import *
from qtsalome import *

__all__ = [
           "Circle",
          ]

class Circle( Model ):

   def __init__( self, name, center, radius, controller ):
       """Constructor"""

       Model.__init__( self,controller )
       self._name = name
       self._center = center
       self._radius = radius
       self.addTreeWidgetItem( self.getName(), controller )
       self.addGraphicScene( controller )
       pass

   def getCenter( self ):
       return self._center[0], self._center[1]

   def setCenter( self, center ):
       self._center = center
       pass

   def getRadius( self ):
       return self._radius

   def setRadius( self, radius ):
       self._radius = radius

   def addTreeWidgetItem( self, name, controller ):
       from CircleTreeWidgetItem import CircleTreeWidgetItem
       from TreeWidgetItem import TreeWidgetItem

       myTreeWidgetItem = CircleTreeWidgetItem( name, controller, ["Show", "Rename", "Delete"] )
       newTreeWidgetItem = TreeWidgetItem( str(self.getCenter()[0]) + ':' + str(self.getCenter()[1]), controller, ["Edit"] )
       myTreeWidgetItem.addChild( newTreeWidgetItem )
       newTreeWidgetItem = TreeWidgetItem( str(self.getRadius()), controller, ["Edit"] )
       myTreeWidgetItem.addChild( newTreeWidgetItem )
       myTreeWidgetItem.setModel( self )
       self.getViews().append( myTreeWidgetItem )
       return myTreeWidgetItem

   def addGraphicScene( self, controller ) :
       from CircleGraphicsScene import CircleGraphicsScene

       myGraphicsScene = CircleGraphicsScene( controller )
       myGraphicsScene.setModel( self )
       self.getViews().append( myGraphicsScene )
       return myGraphicsScene

   def save( self ):
       pass

pass
