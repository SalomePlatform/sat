from qtsalome import *

class Dialog( QDialog ) :

   def __init__( self, helpFile, controller, widgetDialogBox ) :
       """Constructor"""

       # Initializing parent widget
       QDialog.__init__( self )

       # Setting attributes
       self.setObjectName( "Dialog" )
       self.setWindowTitle( "Dialog data" )
       self._helpFile = helpFile
       self._controller = controller
       self._widgetDialogBox = widgetDialogBox

       # Setting layouts
       self.mainLayout = QVBoxLayout( self )
       self.h1 = QHBoxLayout( self )
       self.h2 = QHBoxLayout( self )
       self.mainLayout.addLayout( self.h1 )
       self.mainLayout.addLayout( self.h2 )
       self.v11 = QVBoxLayout( self)
       self.v12 = QVBoxLayout( self )
       self.h1.addLayout( self.v11 )
       self.h1.addLayout( self.v12 )

       # Filling layouts with standard widgets( common to all childre )
       self.fillStandardWidgets()
       # Adding special widgets to layouts( special to each child )
       self.addSpecialWidgets()

       # Connecting widgets to slots
       self.connectSlots()
       pass

   def getController( self ) :
       return self._controller

   def fillStandardWidgets( self ) :

       lName = QLabel( "Name", self )
       self.v11.addWidget( lName )

       self.entryName = QLineEdit( self )
       self.v12.addWidget( self.entryName )

       #Setting buttons
       self.bApply = QPushButton( "Apply", self )
       self.h2.addWidget( self.bApply )
       self.bClose = QPushButton( "Close", self )
       self.h2.addWidget( self.bClose )
       self.bHelp = QPushButton( "Help", self )
       self.h2.addWidget( self.bHelp )
       pass

   def addSpecialWidgets( self ) :
       print 'Virtual method'
       pass

   def connectSlots( self ) :
       self.bApply.clicked.connect(self.apply)
       self.bHelp.clicked.connect(self.help)
       self.bClose.clicked.connect(self.close)
       pass

   def apply( self ) :

       self.retrieveUserEntries()
       if not self.checkUserEntries() :
          QMessageBox.warning( self, 'information faillure', self.errMessage )
          return
       self.execApply()
       return

   def retrieveUserEntries( self ) :
       self.name = str( self.entryName.text() )
       pass

   def checkUserEntries( self ) :
       if self.name == "" :
          self.errMessage = 'All attributes must be filled'
          return False
       return True

   def execApply( self ) :
       print 'Virtual method'
       pass

   def reInitializeDialog( self ) :
       print 'Virtual method'
       pass

   def help( self ) :
       import os
       os.system( 'firefox ' + self._helpFile + '&' )
       pass

   def close( self ) :
       self._widgetDialogBox.close()
       pass

pass
