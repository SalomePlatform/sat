from DialogEdit import *
from qtsalome import *

class EditCenterDialog( DialogEdit ) :

   def __init__( self, helpFile, controller, widgetDialogBox, model, oldCenter ) :
       """Constructor"""

       # Initializing parent widget
       DialogEdit.__init__( self, helpFile, controller, widgetDialogBox )

       self._model = model

       # Reading oldX and oldY
       oldX = ""
       oldY = ""
       i = 0
       while oldCenter[i] != ':' :
          oldX += oldCenter[i]
          i += 1
          pass
       for j in range( i+1, len(oldCenter) ) :
          oldY += oldCenter[j]
          pass
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
       newX = float( self.newX )
       newY = float( self.newY )
       newCenter = newX, newY
       self.getController().editCenter( self._model, newCenter )
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
