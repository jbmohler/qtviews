

from qtviews import *
from PyQt4 import QtCore, QtGui

class CatWindow(QtGui.QWidget):
    title = 'Cat Window'
    appType = 'CatWindow'
    settingsKey = 'CatWindow'

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(QtGui.QLabel('label for {0}'.format(self.title)))

class PigWindow(QtGui.QWidget):
    title = 'Pig Window'
    appType = 'PigWindow'
    settingsKey = 'PigWindow'

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(QtGui.QLabel('label for {0}'.format(self.title)))

class Main(QtGui.QMainWindow, TabbedWorkspaceMixin):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.initTabbedWorkspace()
        self.updateViewFactory({"Pig": PigWindow, "Cat": CatWindow})
        self.setWindowTitle('Docked Window Test')
        self.setMinimumSize(QtCore.QSize(300,300))

        self.loadView("Main", 
                defaultTabs=["Pig", "Cat"])

app = QtGui.QApplication([])
app.setOrganizationName("Mohler")
app.setOrganizationDomain("kiwistrawberry.us")
app.setApplicationName("DockerTest")

w = Main()
w.show()
app.exec_()
