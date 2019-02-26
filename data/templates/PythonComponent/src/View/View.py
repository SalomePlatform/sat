class View() :

   def __init__( self, controller ) :
       """Constructor"""

       self._model = None
       self._controller = controller
       pass

   def getModel( self ) :
       return self._model

   def setModel( self, model ) :
       self._model = model
       pass

   def getController( self ) :
       return self._controller

   def setController( self, controller ) :
       self._controller = controller
       pass

   def editName( self, name ) :
       model = self.getModel()
       self._controller.editName( model, name )
       pass

   def update( self, mode ) :
       print 'Virtual method'
       pass

pass
