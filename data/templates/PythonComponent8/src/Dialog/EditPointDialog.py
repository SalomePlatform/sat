from DialogEdit import *
from qtsalome import *

class EditPointDialog( DialogEdit ) :

   def __init__( self, helpFile, controller, widgetDialogBox, model, oldPoint, pointRange  ) :
       """Constructor"""

       #Initializing parent widget
       DialogEdit.__init__( self, helpFile, controller, widgetDialogBox )

       self._model = model

       #Reading oldX and oldY
       oldX = ""
       oldY = ""
       i = 0
       while oldPoint[i] != ':' :
          oldX += oldPoint[i]
          i += 1
          pass
       for j in range( i+1, len(oldPoint) ) :
          oldY += oldPoint[j]
          pass
       self.pointRange = pointRange
       self.entryX.setText( oldX )
       self.entryY.setText( oldY )
       pass

   def addSpecialWidgets( self ) :
       floatValidator = QDoubleValidator( self )

       lX = QLabel( "X", self )
       self.v11.addWidget( lX )
       lY = QLabel( "Y", self )
       self.v11.addWidget( lY )

       self.entryX = QLineEdit( self )
       self.entryX.setValidator( floatValidator )
       self.v12.addWidget( self.entryX )
       self.entryY = QLineEdit( self )
       self.entryY.setValidator( floatValidator )
       self.v12.addWidget( self.entryY )
       pass

   def execApply( self ) :
       pointRange = self.pointRange
       newX = float( self.newX )
       newY = float( self.newY )
       newPoint = newX, newY
       self.getController().editPoint( self._model, newPoint, pointRange )
       return


   def retrieveUserEntries( self ) :
       self.newX= str( self.entryX.text() )
       self.newY= str( self.entryY.text() )
       pass

   def checkUserEntries( self ) :
       if self.newX == "" or self.newY == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       return True

pass
