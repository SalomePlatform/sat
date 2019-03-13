from View import *
from qtsalome import *

class TreeWidgetItem( View, QTreeWidgetItem ) :

   def __init__( self, name, controller, actionsList ) :
       """Constructor"""

       View.__init__( self, controller )
       self._name = [ name ]
       QTreeWidgetItem.__init__( self, self._name )
       self._actionsList = actionsList
       pass

   def getActionsList( self ) :
       return self._actionsList

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
          self.addToGlobalTree( self )
          pass
       elif mode == 'modification' :
          self.editInGlobalTree( self )
          pass
       elif mode == 'supression' :
          self.removeFromGlobalTree( self )
          pass
       else :
          return

   def addToGlobalTree( self, treeWidgetItem ) :
       globalTree = self.getController().getMainFrame().getGlobalTree()
       globalTree.addTopLevelItem( treeWidgetItem )
       pass

   def editInGlobalTree( self, treeWidgetItem ) :
       print('Virtual')
       pass

   def removeFromGlobalTree( self, treeWidgetItem ) :
       globalTree = self.getController().getMainFrame().getGlobalTree()
       globalTree.takeTopLevelItem( globalTree.indexOfTopLevelItem(treeWidgetItem) )
       pass

pass
