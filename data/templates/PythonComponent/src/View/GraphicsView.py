from Polyline import Polyline
from Circle import Circle
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class GraphicsView( QGraphicsView ) :

   def __init__( self, scene ) :
       QGraphicsView.__init__( self, scene )
       self.setMouseTracking( True )
       self._selectedItem = None
       self.connect( self, SIGNAL("moved(QPointF)"), self.execMouseMoveEvent )
       self.connect( self, SIGNAL("released(QPointF)"), self.execMouseReleaseEvent )
       pass

   def mousePressEvent( self, mouseEvent ) :
       QGraphicsView.mousePressEvent( self, mouseEvent )
       if self.scene() is None : return
       self._selectedItem = self.scene().mouseGrabberItem()
       pass

   def mouseMoveEvent( self, mouseEvent ) :
       QGraphicsView.mouseMoveEvent( self, mouseEvent )
       pt = mouseEvent.pos()
       currentPos = self.mapToScene( pt )
       self.emit( SIGNAL("moved(QPointF)"), currentPos )
       pass

   def mouseReleaseEvent( self, mouseEvent ) :
       QGraphicsView.mouseReleaseEvent( self, mouseEvent )
       if mouseEvent.button() == Qt.LeftButton :
          pt = mouseEvent.pos()
          newPos = self.mapToScene( pt )
          self.emit( SIGNAL("released(QPointF)"), newPos )
          self._selectedItem = None
          pass
       pass

   def execMouseMoveEvent( self, currentPos ) :
       if self._selectedItem is None : return
       selectedIndex = self._selectedItem.getIndex()
       newX = currentPos.x()
       newY = currentPos.y()
       newPoint = newX, newY
       model = self.scene().getModel()
       pen = QPen( QColor("red") )
       if isinstance( model, Polyline ) :
          #Previsualisation
          if selectedIndex == 0 :
             nextPoint = model.getPoints()[ selectedIndex+1 ]
             xNext = nextPoint[0]
             yNext = nextPoint[1]
             self.scene().addLine( newX, newY, xNext, yNext, pen )
             pass
          elif selectedIndex == len( model.getPoints()) - 1 :
             previousPoint = model.getPoints()[ selectedIndex-1 ]
             xPrevious = previousPoint[0]
             yPrevious = previousPoint[1]
             self.scene().addLine( xPrevious, yPrevious, newX, newY, pen )
             pass
          else :
             previousPoint = model.getPoints()[ selectedIndex-1 ]
             xPrevious = previousPoint[0]
             yPrevious = previousPoint[1]
             self.scene().addLine( xPrevious, yPrevious, newX, newY, pen )
             nextPoint = model.getPoints()[ selectedIndex+1 ]
             xNext = nextPoint[0]
             yNext = nextPoint[1]
             self.scene().addLine( newX, newY, xNext, yNext, pen )
             pass
          pass
       elif isinstance( model, Circle ) :
          #Previsualisation
          radius = float( model.getRadius() )
          rect = QRectF( newX-radius, newY-radius, 2*radius, 2*radius )
          circleItem = QGraphicsEllipseItem()
          circleItem.setPen( pen )
          circleItem.setRect( rect )
          self.scene().addItem( circleItem )
          pass
       pass

   def execMouseReleaseEvent( self, newPos ) :
       if self._selectedItem is None : return
       selectedIndex = self._selectedItem.getIndex()
       newX = newPos.x()
       newY = newPos.y()
       newPoint = newX, newY
       model = self.scene().getModel()
       if isinstance( model, Polyline ) :
          self.scene().getController().editPoint( model, newPoint, selectedIndex )
          pass
       elif isinstance( model, Circle ) :
          self.scene().getController().editCenter( model, newPoint )
          pass
       pass

pass
