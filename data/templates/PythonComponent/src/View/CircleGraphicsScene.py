from GraphicsScene import GraphicsScene
from qtsalome import *
from GraphicsRectItem import GraphicsRectItem

class CircleGraphicsScene(  GraphicsScene ) :

   def __init__( self, controller ) :
       GraphicsScene.__init__( self, controller )
       pass

   def draw( self ) :

       import math

       center = self._model.getCenter()
       radius = float( self._model.getRadius() )
       xCenter = float( center[0] )
       yCenter = float( center[1] )

       #Drawing the center as a small rectangle
       centerItem = GraphicsRectItem( xCenter-0.1, yCenter-0.1, 0.2, 0.2, None )
       self.addItem( centerItem )
       #Drawing the circle
       rect = QRectF( xCenter-radius, yCenter-radius, 2*radius, 2*radius )
       circleItem = QGraphicsEllipseItem()
       circleItem.setRect( rect )
       self.addItem( circleItem )
       pass

pass
