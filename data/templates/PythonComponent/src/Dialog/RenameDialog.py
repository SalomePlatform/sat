from DialogEdit import *
from qtsalome import *

class RenameDialog( DialogEdit ) :

   def __init__( self, helpFile, controller, widgetDialogBox, model, oldName  ) :
       """Constructor"""

       # Initializing parent widget
       DialogEdit.__init__( self, helpFile, controller, widgetDialogBox )

       self._model = model
       self.entryName.setText( oldName )
       pass

   def addSpecialWidgets( self ) :
       lName = QLabel( "Name", self )
       self.v11.addWidget( lName )
       self.entryName = QLineEdit( self )
       self.v12.addWidget( self.entryName )
       pass

   def execApply( self ) :
       newName = self.newName
       self.getController().editName( self._model, newName )
       return

   def retrieveUserEntries( self ) :
       self.newName = str( self.entryName.text() )
       pass

   def checkUserEntries( self ) :
       if self.newName == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       return True

pass
