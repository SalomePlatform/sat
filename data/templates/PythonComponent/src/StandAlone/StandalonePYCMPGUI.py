import sys

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from Controller import Controller
from Desktop import Desktop

def main( args ) :
    Appli = QApplication( args )
    MainFrame = Desktop()
    myController = Controller( MainFrame )
    MainFrame.setController( myController )
    MainFrame.show()
    Appli.exec_()

if __name__ == "__main__" :
   main( sys.argv )
   pass

