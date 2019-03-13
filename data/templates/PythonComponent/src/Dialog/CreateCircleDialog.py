from Dialog import *
from qtsalome import *

class CreateCircleDialog( Dialog ) :

   def __init__( self, helpFile, controller, widgetDialogBox ) :
       """Constructor"""

       # Initializing parent widget
       Dialog.__init__( self, helpFile, controller, widgetDialogBox )

       # Setting default name
       nbCircles = controller.getNbCircles()
       self.entryName.setText( "circle_" + str(nbCircles+1) )
       pass

   def addSpecialWidgets( self ) :
       floatValidator = QDoubleValidator( self )

       lxCenter = QLabel( "xCenter", self )
       self.v11.addWidget( lxCenter )
       lyCenter = QLabel( "yCenter", self )
       self.v11.addWidget( lyCenter )
       lRadius = QLabel( "Radius", self )
       self.v11.addWidget( lRadius )

       self.entryxCenter = QLineEdit( self )
       self.entryxCenter.setValidator( floatValidator )
       self.entryxCenter.setText( "0" )
       self.v12.addWidget( self.entryxCenter )
       self.entryyCenter = QLineEdit( self )
       self.entryyCenter.setValidator( floatValidator )
       self.entryyCenter.setText( "0" )
       self.v12.addWidget( self.entryyCenter )
       self.entryRadius = QLineEdit( self )
       self.entryRadius.setValidator( floatValidator )
       self.entryRadius.setText( "10" )
       self.v12.addWidget( self.entryRadius)
       pass

   def execApply( self ) :
       name = self.name
       center = float(self.xCenter), float(self.yCenter)
       radius = float( self.radius )
       self.getController().createCircle( name, center, radius )
       self.reInitializeDialog()
       return

   def retrieveUserEntries( self ) :
       self.name = str( self.entryName.text() )
       self.xCenter = str( self.entryxCenter.text() )
       self.yCenter = str( self.entryyCenter.text() )
       self.radius = str( self.entryRadius.text() )
       pass

   def checkUserEntries( self ) :
       if self.name == "" or self.xCenter == "" or self.yCenter == "" or self.radius == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       return True

   def reInitializeDialog( self ) :
       nbCircles = self.getController().getNbCircles()
       self.entryName.setText( "circle_" + str(nbCircles+1) )
       self.entryxCenter.setText( "0" )
       self.entryyCenter.setText( "0" )
       self.entryRadius.setText( "10" )
       pass

pass
