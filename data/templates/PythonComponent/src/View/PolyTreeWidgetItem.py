from View import *
from TreeWidgetItem import TreeWidgetItem
from qtsalome import *

class PolyTreeWidgetItem( TreeWidgetItem ) :

   def __init__( self, name, controller, actionsList ) :
       """Constructor"""

       TreeWidgetItem.__init__( self, name, controller, actionsList )
       pass

   def editInGlobalTree( self, treeWidgetItem ) :
       name = self.getModel().getName()
       treeWidgetItem.setText( 0 , name )

       points = self._model.getPoints()
       for i in range( len(points) ) :
          point = points[i]
          xPoint = point[0]
          yPoint = point[1]
          relatedItem = treeWidgetItem.child( i )
          relatedItem.setText( 0 , str(xPoint) + ":" + str(yPoint) )
          pass
       pass

pass
