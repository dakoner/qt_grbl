import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from .state import State

class QtGrblQObject(QtCore.QObject):
    messageSignal = QtCore.pyqtSignal(str)
    statusSignal = QtCore.pyqtSignal(dict)
    stateSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.changeState(State.STATE_INIT)

    def connected(self):
        print("connected")
        self.changeState(State.STATE_READY)

        self.status_timer = QtCore.QTimer()
        self.status_timer.timeout.connect(self.do_status)
        self.status_timer.start(1000)

    def changeState(self, state):
        self.state = state
        name = State(self.state).name
        self.stateSignal.emit(name)
        
    def do_status(self):
        if self.state in (State.STATE_READY, State.STATE_SENDING_COMMAND):        
            self.internal_do_status()
        else:
            print("Can't get state when not connected", self.state)

    def send_line(self, line):
        if self.state != State.STATE_READY:
            print("Cannot send line when not ready")
            return False
        print("send line", line)
        self.internal_send_line(line)
        return True

    def internal_do_status(self):
        print("Unsupported: internal_do_status")

    def internal_send_line(self, line):
        print("Unsupported: internal_send_line:", line)