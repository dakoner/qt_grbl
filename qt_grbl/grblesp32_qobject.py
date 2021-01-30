import sys

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from qt_grbl_qobject import QtGrblQObject
from state import State

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

        self.client =  QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.error)
        self.client.connected.connect(self.connected)

        self.client.open(QUrl(f"ws://{HOSTNAME}:81"))
        self.client.textMessageReceived.connect(self.onText)
        self.client.binaryMessageReceived.connect(self.onBinary)

        self.manager = QtNetwork.QNetworkAccessManager()


    def onText(self, message):
        if message.startswith("CURRENT_ID"):
            self.current_id = message.split(':')[1]
            print("Current id is:", self.current_id)
        elif message.startswith("ACTIVE_ID"):
            active_id = message.split(':')[1]
            if self.current_id != active_id:
                print("Warning: different active id.")
        elif message.startswith("PING"):
            ping_id = message.split(":")[1]
            if ping_id != self.current_id:
                print("Warning: ping different active id.")


    def onBinary(self, messages):
        messages = str(messages, 'ascii')
        for message in messages.split("\r\n"):
            if message == '':
                continue
            print("Got message: '%s'" % message)
            if self.state == State.STATE_SENDING_COMMAND:
                print("waiting for an ok")
            if message == 'ok':
                print("Got ok in state", self.state)
                if self.state == State.STATE_SENDING_COMMAND:
                    self.changeState(State.STATE_READY)
                else:
                    print("Got ok when didn't expect one!")
            else:
                results = parseStatus(message)
                if results:
                    self.statusSignal.emit(results)
                else:
                    self.messageSignal.emit(message)
        
    def internal_do_status(self):
        request = QtNetwork.QNetworkRequest(url=QtCore.QUrl(f"http://{HOSTNAME}/command?commandText=?"))
        self.replyObject = self.manager.get(request)

    def internal_send_line(self, line):
        request = QtNetwork.QNetworkRequest()
        url = QtCore.QUrl(f"http://{HOSTNAME}/command?commandText={line}")
        request.setUrl(url)
        self.manager.get(request)
        self.changeState(State.STATE_SENDING_COMMAND)
        return True

    def error(self, error_code):
        print("error code: {}".format(error_code))
        if error_code == 1:
            print(self.client.errorString())

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    client = GRBLESP32Client()

    app.exec_()