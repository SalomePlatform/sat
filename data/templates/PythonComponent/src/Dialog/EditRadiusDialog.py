from DialogEdit import *
from qtsalome import *

class EditRadiusDialog( DialogEdit ) :

   def __init__( self, helpFile, controller, widgetDialogBox, model, oldRadius  ) :
       """Constructor"""

       #Initializing parent widget
       DialogEdit.__init__( self, helpFile, controller, widgetDialogBox )

       self._model = model
       self.entryRadius.setText( oldRadius )
       pass

   def addSpecialWidgets( self ) :
       floatValidator = QDoubleValidator( self )

       lRadius = QLabel( "Radius", self )
       self.v11.addWidget( lRadius )
       self.entryRadius = QLineEdit( self )
       self.entryRadius.setValidator( floatValidator )
       self.v12.addWidget( self.entryRadius )
       pass

   def execApply( self ) :
       newRadius = self.newRadius
       self.getController().editRadius( self._model, newRadius )
       return


   def retrieveUserEntries( self ) :
       self.newRadius = str( self.entryRadius.text() )
       pass

   def checkUserEntries( self ) :
       if self.newRadius == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       return True

pass
