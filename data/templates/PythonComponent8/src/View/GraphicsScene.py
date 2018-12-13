from View import *
from qtsalome import *

class GraphicsScene( View, QGraphicsScene ) :

   def __init__( self, controller ) :
       """Constructor"""

       View.__init__( self, controller )
       QGraphicsScene.__init__( self )
       pass

   def getRect( self ) :
       rect = QRectF( 0, 0, self.width(), self.height() )
       return rect

   def editPoint( self, oldPoint, newPoint ) :
       polyline = self.getModel()
       self.getController().editPoint( polyline, oldPoint, newPoint )
       pass

   def editCenter( self, center ) :
       circle = self.getModel()
       self.getController().editCenter( circle, center )
       pass

   def editRadius( self, radius ) :
       circle = self.getModel()
       self.getController().editRadius( circle, radius )
       pass

   def update( self, mode ) :
       if mode == 'creation' :
          self.showInGlobalGraphicsView()
          pass
       elif mode == "showing" :
          self.showInGlobalGraphicsView()
       elif mode == 'modification' :
          self.undraw()
          self.showInGlobalGraphicsView()
          pass
       elif mode == 'supression' :
          self.removeFromGlobalGraphicsView()
          pass
       else :
          return

   def showInGlobalGraphicsView( self ) :
       self.draw()
       self.getController().getMainFrame().updateGlobalGraphicsView( self  )
       pass

   def removeFromGlobalGraphicsView( self ) :
       self.getController().getMainFrame().updateGlobalGraphicsView( None  )
       pass

   def draw( self ) :
       print 'Virtual method'
       pass

   def undraw( self ) :
       for item in self.items() :
          self.removeItem( item )
          pass
       pass

pass
