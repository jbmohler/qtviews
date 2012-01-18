##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from PyQt4 import QtCore, QtGui

class WindowMeta(object):
    def __init__(self, title, appType, settingsKey=None):
        self.title = title
        self.appType = appType
        if settingsKey is None:
            self.settingsKey = appType
        else:
            self.settingsKey = settingsKey

class Docker(QtGui.QDockWidget):
    def __init__(self, mainWindow, child):
        QtGui.QDockWidget.__init__(self)
        self.child = child
        self.mainWindow = mainWindow
        self.setObjectName(child._docker_meta.title)
        self.setWidget(child)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pnt: 
                self.mainWindow.workspaceContextMenu(self.child, pnt))

class TabbedWorkspaceMixin(object):
    def initTabbedWorkspace(self):
        self.workspace = QtGui.QTabWidget()
        self.setCentralWidget(self.workspace)
        self.workspace.setDocumentMode(True)
        self.workspace.setTabsClosable(True)
        self.workspace.tabCloseRequested.connect(self.closeTab)

        self.workspace.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.workspace.customContextMenuRequested.connect(self.workspaceContextMenu01)

    def viewFactory(self, klass, settingsKey=None):
        """
        :param klass: view factory function for specific views
        :param settingsKey: an option key string for where to find the settings
            for this view
        """
        c = klass(settingsKey)
        self.addWorkspaceWindow(c.widget(), c.title(), c.settingsKey)

    def addWorkspaceWindow(self, widget, title, appType, settingsKey=None):
        """
        Add a dock managed window.  Tabify or dock as according to settings.
        """
        widget._docker_meta = WindowMeta(title, appType, settingsKey)
        self.workspace.addTab(widget, name)
        self.workspace.setCurrentWidget(widget)
        widget.setWindowTitle(name)
        widget.show()
        widget.setFocus()

    def workspaceWindowByKey(self, settingsKey):
        tabs = [tab for tab in self.tabsCollection() if
                tab._docker_meta.settingsKey==settingsKey]
        docks = [d for d in self.docked if d._docker_meta.settingsKey==settingsKey]
        if len(tabs+docks):
            return (tabs+docks)[0]
        return None

    def dockWorkspaceWindow(self, settingsKey):
        """
        Remove a tabbed window from the tab widget and add it as a dock window.
        """
        w = self.workspaceWindowByKey(settingsKey)
        if w is not None:
            self.docked.append(w)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, Docker(self, w))

    def undockWorkspaceWindow(self, settingsKey):
        """
        Remove a docked window from any docking area and add it to the central
        tab bar.
        """
        w = self.workspaceWindowByKey(settingsKey)
        if w is not None:
            self.docked.remove(w)
            self.addWorkspaceWindow(w, w.objectName(), "something")

    def workspaceContextMenu(self, w, pnt):
        self.menu = QtGui.QMenu()
        # rename, close, dock
        #a = self.menu.addAction("Close")
        #a.triggered.connect(lambda check: self.closeTab(self.workspace.currentIndex()))

        a = self.menu.addAction("Tabify")
        a.triggered.connect(lambda check, key=w._docker_meta.settingsKey:
                self.undockWorkspaceWindow(key))

        #self.menu.addAction(self.workspace.currentWidget().model.renameAction)
        self.menu.popup(self.workspace.mapToGlobal(pnt))

    def workspaceContextMenu01(self, pnt):
        tb = self.workspace.tabBar()
        if tb.tabAt(pnt) == self.workspace.currentIndex():
            self.menu = QtGui.QMenu()

            w = self.workspace.currentWidget()
            # rename, close, dock
            a = self.menu.addAction("Close")
            a.triggered.connect(lambda check: self.closeTab(self.workspace.currentIndex()))

            a = self.menu.addAction("Add docked")
            a.triggered.connect(lambda check, key=w._docker_meta.settingsKey:
                    self.dockWorkspaceWindow(key))

            #self.menu.addAction(self.workspace.currentWidget().model.renameAction)
            self.menu.popup(self.workspace.mapToGlobal(pnt))

    def closeTab(self, index):
        self.workspace.removeTab(index)

    def tabsInWindowMenu(self):
        for i in range(self.workspace.count()):
            child = self.workspace.widget(i)
            if i < 9:
                text = self.tr("&{0} {1}".format(i+1, child.windowTitle()))
            else:
                text = self.tr("&{1}".format(child.windowTitle()))

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.workspace.currentWidget())
            action.triggered.connect(lambda checked,
                    key=child._docker_meta.settingsKey: self.selectTab(key))

    def tabsCollection(self):
        for i in range(self.workspace.count()):
            yield self.workspace.widget(i)

    def selectTab(self, key):
        desired = [tab for tab in self.tabsCollection() if
                tab._docker_meta.settingsKey==key]
        if len(desired):
            self.workspace.setCurrentWidget(desired[0])
        return desired[0] if len(desired)>0 else None

