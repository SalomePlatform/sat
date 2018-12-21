from qtsalome import *
from Menu import Menu
from RenameDialog import RenameDialog
from EditPointDialog import EditPointDialog
from EditCenterDialog import EditCenterDialog
from EditRadiusDialog import EditRadiusDialog
from Polyline import Polyline
from Circle import Circle
from SalomePyQt import SalomePyQt
from libSALOME_Swig import SALOMEGUI_Swig

#########################################
# Global variables
#########################################

sgPyQt = SalomePyQt()
sg = SALOMEGUI_Swig()
sgDesktop = sgPyQt.getDesktop()

#########################################

class TreeWidget( QTreeWidget ) :

   def __init__( self, desktop ) :
       """Constructor"""

       QTreeWidget.__init__( self )
       self._desktop = desktop

       #Creating popup menu
       self.setContextMenuPolicy( Qt.CustomContextMenu )
       self.customContextMenuRequested[QPoint].connect(self.createPopups)
       pass

   def createPopups( self, point ) :
       item = self.itemAt( point )
       if item is None : return
       self.menu = Menu( item )
       for action in item.getActionsList():
          if action == "Show" :
             self.menu.addAction(action).triggered.connect(self.show)
             pass
          elif action == 'Rename' :
             self.menu.addAction(action).triggered.connect(self.showRenameDialog)
             pass
          elif action == 'Delete' :
             self.menu.addAction(action).triggered.connect(self.delete)
             pass
          else :
             self.menu.addAction(action).triggered.connect(self.showEditDialog)
             pass
          pass
       self. menu.exec_( QCursor.pos() )
       pass

   def show( self ) :
       model = self.menu.getItem().getModel()
       controller = self._desktop.getController()
       controller.showModel( model )
       pass

   def showRenameDialog( self ) :
       model = self.menu.getItem().getModel()
       oldName = model.getName()
       widgetDialogBox = QDockWidget( sgDesktop )
       myDialog = RenameDialog( "www.google.fr", self._desktop.getController(), widgetDialogBox, model, oldName )
       widgetDialogBox.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       widgetDialogBox.setWidget( myDialog )
       widgetDialogBox.setWindowTitle( "Object renaming" )
       sgDesktop.addDockWidget( Qt.LeftDockWidgetArea, widgetDialogBox )
       pass

   def delete( self ) :
       answer = QMessageBox.question( self, 'Confirmation', 'Do you really want to remove the selected curve ?' , QMessageBox.Yes | QMessageBox.No )
       if answer == QMessageBox.Yes :
          model = self.menu.getItem().getModel()
          controller = self._desktop.getController()
          controller.removeModel( model )
          pass
       pass

   def showEditDialog( self ) :
       item = self.menu.getItem()
       parentItem = item.parent()
       parentModel = parentItem.getModel()
       widgetDialogBox = QDockWidget( sgDesktop )
       if isinstance( parentModel, Polyline ) :
          pointRange = parentItem.indexOfChild( item )
          oldPoint = item.text( 0 )
          myDialog = EditPointDialog( "www.google.fr", self._desktop.getController(), widgetDialogBox, parentModel, oldPoint, pointRange )
          pass
       elif isinstance( parentModel, Circle ) :
          selectedRange = parentItem.indexOfChild( item )
          oldSelected = item.text( 0 )
          if selectedRange == 0 : myDialog = EditCenterDialog( "www.google.fr", self._desktop.getController(), widgetDialogBox, parentModel, oldSelected )
          elif selectedRange == 1 : myDialog = EditRadiusDialog("www.google.fr",self._desktop.getController(),widgetDialogBox,parentModel,oldSelected)
          else : pass
          pass
       else : pass

       widgetDialogBox.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       widgetDialogBox.setWidget( myDialog )
       widgetDialogBox.setWindowTitle( "Object edition" )
       sgDesktop.addDockWidget( Qt.LeftDockWidgetArea, widgetDialogBox )
       pass

pass
