from qtviews import *
from PySide2 import QtCore, QtWidgets

class CatWindow(QtWidgets.QWidget):
    title = 'Cat Window'
    appType = 'CatWindow'
    settingsKey = 'CatWindow'

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('label for {0}'.format(self.title)))

class PigWindow(QtWidgets.QWidget):
    title = 'Pig Window'
    appType = 'PigWindow'
    settingsKey = 'PigWindow'

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('label for {0}'.format(self.title)))

class Main(QtWidgets.QMainWindow, TabbedWorkspaceMixin):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.initTabbedWorkspace()
        self.updateViewFactory({"Pig": PigWindow, "Cat": CatWindow})
        self.setWindowTitle('Docked Window Test')
        self.setMinimumSize(QtCore.QSize(300,300))

        self.loadView("Main", 
                defaultTabs=["Pig", "Cat"])


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setOrganizationName("Mohler")
    app.setOrganizationDomain("kiwistrawberry.us")
    app.setApplicationName("DockerTest")

    w = Main()
    w.show()
    app.exec_()
