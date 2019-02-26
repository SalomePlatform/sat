from Dialog import Dialog
from qtsalome import *

class CreatePolylineDialog( Dialog ) :

   def __init__( self, helpFile, controller, widgetDialogBox  ) :
       """Constructor"""

       #Initializing parent widget
       Dialog.__init__( self, helpFile, controller, widgetDialogBox )

       #Setting default name
       nbPolylines = controller.getNbPolylines()
       self.entryName.setText( "polyline_" + str(nbPolylines+1) )
       pass

   def addSpecialWidgets( self ) :

       intValidator = QIntValidator( self )

       lNbPoints = QLabel( "Number of points", self )
       self.v11.addWidget( lNbPoints )

       self.entryNbPoints = QLineEdit( self )
       self.entryNbPoints.setValidator( intValidator )
       self.entryNbPoints.setText( "10" )
       self.v12.addWidget( self.entryNbPoints )
       pass

   def execApply( self ) :
       name = self.name
       nbPoints = int( self.nbPoints )
       self.getController().createPolyline( name, nbPoints )
       self.reInitializeDialog()
       return


   def retrieveUserEntries( self ) :
       self.name = str( self.entryName.text() )
       self.nbPoints = str( self.entryNbPoints.text() )
       pass

   def checkUserEntries( self ) :
       if self.name == "" or self.nbPoints == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       if int( self.nbPoints ) > 10 :
          self.errMessage = 'The number of points must not exceed 10'
          return False
       return True

   def reInitializeDialog( self ) :
       nbPolylines = self.getController().getNbPolylines()
       self.entryName.setText( "polyline_" + str(nbPolylines+1) )
       self.entryNbPoints.setText( "10" )
       pass

pass
