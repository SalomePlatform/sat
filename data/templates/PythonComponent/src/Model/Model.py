from View import *

class Model:

   def __init__( self, controller ):
       """Constructor"""

       self._name = None
       self._views = []
       pass

   def getName( self ):
       return self._name

   def setName( self, name ):
       self._name = name
       pass

   def getViews( self ) :
       return self._views

   def addView( self ) :
       myView = View()
       self._views.append( myView )
       return myView

   def updateViews( self, mode ) :
       for view in self._views : view.update( mode )

   def save( self ) :
       print('Virtual method')
       pass

pass
