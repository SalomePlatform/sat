from Controller import Controller
from Desktop import Desktop
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys

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

