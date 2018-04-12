from qtsalome import *

class GraphicsRectItem( QGraphicsRectItem ) :

   def __init__( self, x, y, w, h, index ) :
       QGraphicsRectItem.__init__( self, x, y, w, h )
       self._index = index
       self.setFlag( self.ItemIsMovable, True )
       self.setFlag( self.ItemIsSelectable, True )
       pass

   def getIndex( self ) :
       return self._index

pass
