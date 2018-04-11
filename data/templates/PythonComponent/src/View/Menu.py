from qtsalome import *

class Menu( QMenu ) :

   def __init__( self, item ) :
       """Constructor"""

       QMenu.__init__( self )
       self._item = item
       pass

   def getItem( self ) :
       return self._item

pass
