# -*- coding: utf-8 -*-
'''
Created on 18-03-2012

@author: Paweł Jarosz

Adapted from http://stackoverflow.com/questions/2758159/how-to-embed-a-python-interpreter-in-a-pyqt-widget .

Augmented as indicated by Joel B. Mohler.
'''
import os
import atexit

from PySide import QtCore, QtGui

from IPython.zmq.ipkernel import IPKernelApp
from IPython.lib.kernel import find_connection_file, connect_qtconsole
from IPython.frontend.qt.kernelmanager import QtKernelManager
from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.config.application import catch_config_error

class IPythonLocalKernelApp(IPKernelApp):
    """
    IPython kernel application with nonblocking loop, running in dedicated
    thread.  example:

    >>> app = QtGui.QApplication([])
    >>> kernelapp = IPythonLocalKernelApp.instance()
    >>> kernelapp.start()
    >>> namespace = kernelapp.get_user_namespace()
    >>> namespace["QtGui"]=QtGui
    >>> namespace["QtCore"]=QtCore
    >>> app.exec_()
    """
    #DEFAULT_INSTANCE_ARGS starting commandline
    DEFAULT_INSTANCE_ARGS = ['qtconsole','--pylab=inline', '--colors=linux']

    @catch_config_error
    def initialize(self, argv=None):
        super(IPythonLocalKernelApp, self).initialize(argv)
        self.kernel.eventloop = self.loop_qt4_nonblocking

    def loop_qt4_nonblocking(self, kernel):
        """Non-blocking version of the ipython qt4 kernel loop"""
        kernel.timer = QtCore.QTimer()
        kernel.timer.timeout.connect(kernel.do_one_iteration)
        kernel.timer.start(1000*kernel._poll_interval)

    def start(self, argv=DEFAULT_INSTANCE_ARGS):
        """Starts IPython kernel app
            argv: arguments passed to kernel
        """
        self.initialize(argv)
        self.heartbeat.start()
        if self.poller is not None:
            self.poller.start()

        self.kernel.start()

    def get_connection_file(self):
        """Returne current kernel connection file."""
        return self.connection_file

    def get_user_namespace(self):
        """Returns current kernel userspace dict"""
        return self.kernel.shell.user_ns

class IPythonConsoleQtWidget(RichIPythonWidget):
    """
    Ipython console Qt4+ widget
    
    Usage example:
    >>> app = QtGui.QApplication([])
    >>> kernelapp = IPythonLocalKernelApp.instance()
    >>> kernelapp.start()
    >>> namespace = kernelapp.get_user_namespace()
    >>> widget = IPythonConsoleQtWidget()
    >>> widget.set_default_style(colors='linux')
    >>> widget.connect_kernel(connection_file=kernelapp.get_connection_file())
    >>> # if you won't to connect to remote kernel:
    >>> widget.connect_kernel(connection_file='kernel-16098.json')

    >>> widget.show()

    >>> namespace["widget"] = widget
    >>> namespace["QtGui"]=QtGui
    >>> namespace["QtCore"]=QtCore

    >>> app.exec_()
    """
    _connection_file = None

    def __init__(self, *args, **kw):
        RichIPythonWidget.__init__(self, *args, **kw)
        self._existing = True
        self._may_close = False
        self._confirm_exit = False

    def _init_kernel_manager(self):
        km = QtKernelManager(connection_file=self._connection_file, config=self.config)
        km.load_connection_file()
        km.start_channels(hb=self._heartbeat)
        self.kernel_manager = km
        atexit.register(self.kernel_manager.cleanup_connection_file)

    def connect_kernel(self, connection_file, heartbeat=False):
        """
        Connect's to ipython kernel.

        :param connection_file: connection file to use
        :param heartbeat: should start heartbeat server? Workaround for
            problems with inproc embedded kernels (right click save image
            as/save as html kills kernel heartbeat/pool(??) serwer 
        """
        self._heartbeat = heartbeat
        if os.path.exists(connection_file):
            self._connection_file = connection_file
        else:
            self._connection_file = find_connection_file(connection_file)

        self._init_kernel_manager()

    @property
    def user_ns(self):
        # TODO:  I think the precise details of this implementation may depend
        # on the kernel type.
        return self._user_ns

    @user_ns.setter
    def user_ns(self, value):
        self._user_ns = value


def IPythonLocalKernelWidget(colors='linux'):
    """
    Author:  Joel B. Mohler

    >>> w = IPythonLocalKernelWidget()
    >>> w.user_ns["test"] = 1
    """
    kernelapp = IPythonLocalKernelApp.instance()
    kernelapp.start()

    widget = IPythonConsoleQtWidget()
    widget.set_default_style(colors=colors)
    widget.connect_kernel(connection_file=kernelapp.get_connection_file())
    widget.user_ns = kernelapp.get_user_namespace()
    # if you won't to connect to remote kernel:
    # widget.connect_kernel(connection_file='kernel-16098.json')
    return widget