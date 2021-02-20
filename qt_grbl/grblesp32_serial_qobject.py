import sys

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from .qt_grbl_qobject import QtGrblQObject
from PyQt5.QtSerialPort import QSerialPort

from .state import State

HOSTNAME="postscope.local"

def parseStatus(status):
    status = status.strip()
    if not status.startswith("<") or not status.endswith(">"):
        return None
    rest = status[1:-3].split('|')
    state = rest[0]
    results = { 'state': state }
    for item in rest:
        if item.startswith("MPos"):
            m_pos = [float(field) for field in item[5:].split(',')]
            results['m_pos'] = m_pos
        elif item.startswith("Pn"):
            pins = item[3:]
            results['pins'] = pins
    return results

class GRBLESP32Client(QtGrblQObject):
    def __init__(self):
        super().__init__()

        self.serial = QSerialPort()
        self.line = ""
        port = "/dev/ttyUSB0"
        self.serial.setPortName(port)
        if self.serial.open(QtCore.QIODevice.ReadWrite):
            self.serial.setDataTerminalReady(True)
            self.serial.setBaudRate(115200)
            self.serial.readyRead.connect(self.on_serial_read)
            self.serial.write(b"\r\n")
        else:
            print("Failed to open serial port")

    def on_serial_read(self):
        #print("serial read")
        if not self.serial.canReadLine():
            line = self.serial.readLine()
            #print("incomplete line, adding", line)
            self.line += line.data().decode('US_ASCII')
            return
        message = self.line + self.serial.readLine().data().decode('US_ASCII')
        message = message.strip()
        self.line = ""
    
        if message == '':
            return
        print("Got message: '%s'" % message)
        if self.state == State.STATE_SENDING_COMMAND:
            print("waiting for an ok")
        if message == 'ok':
            #print("Got ok in state", self.state)
            self.messageSignal.emit(message)
            if self.state == State.STATE_SENDING_COMMAND:
                self.changeState(State.STATE_READY)
            elif self.state == State.STATE_INIT:
                self.changeState(State.STATE_READY)
            else:
                print("Got ok when didn't expect one!")
        elif message.startswith('error:'):
            print("Got error in state", self.state)
            if self.state == State.STATE_SENDING_COMMAND:
                self.changeState(State.STATE_READY)
            elif self.state == State.STATE_INIT:
                self.changeState(State.STATE_READY)
            else:
                print("Got error when didn't expect one!")
        else:
            results = parseStatus(message)
            if results:
                self.statusSignal.emit(results)
            else:
                self.messageSignal.emit(message)

    def internal_send_line(self, line):
        b = bytearray(line + '\r', 'utf-8')
        self.serial.writeData(b)
        if not line.startswith("$"):
            self.changeState(State.STATE_SENDING_COMMAND)

    def internal_write(self, code):
        self.serial.writeData(bytes([code]))

    def error(self, error_code):
        print("error code: {}".format(error_code))
        if error_code == 1:
            print(self.client.errorString())

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    client = GRBLESP32Client()

    app.exec_()
