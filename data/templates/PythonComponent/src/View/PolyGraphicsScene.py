from GraphicsScene import GraphicsScene
from qtsalome import *
from GraphicsRectItem import GraphicsRectItem

class PolyGraphicsScene(  GraphicsScene ) :

   def __init__( self, controller ) :
       GraphicsScene.__init__( self, controller )
       pass

   def draw( self ) :
       points = self.getModel().getPoints()

       # Drawing the points as small rectangles
       for i in range( len(points) ) :
          point = points[i]
          xPoint = float( point[0] )
          yPoint = float( point[1] )
          # Constructing a rectangle centered on point
          pointItem = GraphicsRectItem( xPoint-0.1, yPoint-0.1, 0.2, 0.2, i )
          self.addItem( pointItem )
          pass

       # Linking the points with lines
       for i in range( len(points) - 1 ) :
          current = points[i]
          next = points[i+1]
          xCurrent = float( current[0] )
          yCurrent = float( current[1] )
          xNext = float( next[0] )
          yNext = float( next[1] )
          line = QLineF( xCurrent, yCurrent, xNext, yNext )
          lineItem = QGraphicsLineItem()
          lineItem.setLine( line )
          self.addItem( lineItem )
          pass
       pass

pass
