from Polyline import Polyline
from Circle import Circle

class Controller() :
    """Manages the Model instances"""

    def __init__( self, MainFrame ) :
        """Constructor"""

        self._models = []
        self._mainFrame = MainFrame
        self._nbPolylines = 0
        self._nbCircles = 0
        pass

    def getModels( self ) :
        return self._models

    def getMainFrame( self ) :
        return self._mainFrame

    def getNbPolylines( self ) :
        return self._nbPolylines

    def setNbPolylines( self, n ) :
        self._nbPolylines = n
        pass

    def getNbCircles( self ) :
        return self._nbCircles

    def setNbCircles( self, n ) :
        self._nbCircles = n
        pass

    def createPolyline( self, name, randomNumberOfPoints ) :
        """Creates a Polyline object nammed name with randomNumberOfPoints points"""

        import random

        # Making randomNumberOfPoints random positionned points
        points = []
        x = random.uniform( 0, randomNumberOfPoints )
        for i in range( randomNumberOfPoints ) :
           x = random.uniform( x, x+randomNumberOfPoints )
           y = random.uniform( 0, x )
           point = x, y
           points.append( point )
           pass

        myPolyline = Polyline( name, points, self )
        self._models.append( myPolyline )
        myPolyline.updateViews( mode = 'creation' )

        self._nbPolylines +=1
        return myPolyline

    def createCircle( self, name, center, radius ) :
        """Creates a Circle object nammed name with center and radius"""

        myCircle = Circle( name, center, radius, self )
        self._models.append( myCircle )
        myCircle.updateViews( mode = 'creation' )

        self._nbCircles +=1
        return myCircle

    def showModel( self, model ) :
        model.updateViews( mode = 'showing' )
        pass

    def editName( self, model, name ) :
        model.setName( name )
        model.updateViews( mode = 'modification' )
        return model

    def editPoint( self, polyline, newPoint, pointRange ) :
        polyline.editPoint( pointRange, newPoint )
        polyline.updateViews( mode = 'modification' )
        return polyline

    def editCenter( self, circle, center ) :
        circle.setCenter( center )
        circle.updateViews( mode = 'modification' )
        return circle

    def editRadius( self, circle, radius ) :
        circle.setRadius( radius )
        circle.updateViews( mode = 'modification' )
        return circle

    def removeModel( self, model ) :
        model.updateViews( mode = 'supression' )
        index = self._models.index( model )
        del model
        pass

    def saveListOfModels( self ) :
        for model in self._models :
           model.save()
           pass
        pass

pass
