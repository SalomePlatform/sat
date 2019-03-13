from View import *
from TreeWidgetItem import TreeWidgetItem
from qtsalome import *

class CircleTreeWidgetItem( TreeWidgetItem ) :

   def __init__( self, name, controller, actionsList ) :
       """Constructor"""

       TreeWidgetItem.__init__( self, name, controller, actionsList )
       pass

   def editInGlobalTree( self, treeWidgetItem ) :
       name = self.getModel().getName()
       treeWidgetItem.setText( 0 , name )
       center = self._model.getCenter()
       xCenter = center[0]
       yCenter = center[1]
       relatedItem = treeWidgetItem.child( 0 )
       relatedItem.setText( 0 , str(xCenter) + ":" + str(yCenter) )

       radius = self._model.getRadius()
       relatedItem = treeWidgetItem.child( 1 )
       relatedItem.setText( 0 , str(radius) )
       pass

pass
