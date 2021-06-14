import sys
import json
import random
import numpy as np
import pyvista as pv

from PyQt5.QtCore import QDataStream, QByteArray, QIODevice
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from PyQt5.QtWidgets import(
    QApplication,
    QDialog,
    QLabel,
    QVBoxLayout
)

class MainWindow(QDialog):
    def __init__(self):
        """Layout is defined here"""
        super().__init__()
        self.setWindowTitle("SERVER")
        self.setFixedSize(250, 100)

        #Label
        self.statusLabel = QLabel("The server is running on port 6789")
        self.generalLayout = QVBoxLayout()
        self.generalLayout.addWidget(self.statusLabel)
        self.setLayout(self.generalLayout)

        #creating data to be sent
        self.dictionary = {}
        self.dictionary["Bar Graph"] = []
        self.dictionary["Curve Graph"] = []
        self.dictionary["BOX"] = []
        self.dictionary["sphere"] = []

        self.setUpServer()

    def setUpServer(self):
        """Setting up the server"""
        self.tcpServer = QTcpServer()
        self.tcpServer.listen(QHostAddress.LocalHost, 6789)

        self.tcpServer.newConnection.connect(self.newConnection)

    def newConnection(self):
        """a connection is established here and is waiting for request"""
        self.clientConnection = self.tcpServer.nextPendingConnection()
        self.clientConnection.disconnected.connect(self.clientConnection.deleteLater)

        self.blockSize = 0
        self.clientConnection.readyRead.connect(self.readRequest)

    def readRequest(self):
        """
        request is read and depending on requirements 
        sepcific 2d or 3d data is sent
        """
        dataStream = QDataStream(self.clientConnection)

        if self.blockSize == 0:
            if self.clientConnection.bytesAvailable() < 2:
                return

            self.blockSize = dataStream.readUInt16()

        if self.clientConnection.bytesAvailable() < self.blockSize:
            return

        self.request = dataStream.readString()

        self.request = json.loads(self.request)
        print(self.request)

        if self.request['dimension'] == '2D':
            self.send2Data()

        else:
            self.send3Data()

    def send2Data(self):
        """dictionary with 2d data is created"""
        limit = int(self.request['range'])
        points = int(self.request['points'])
        print(points)

        yAxis = []
        for _ in range(points):
            yAxis.append(random.randint(1, limit))

        xAxis = [i for i in range(points)]

        dictionary = {}
        dictionary['dimension'] = '2D'
        if self.request['graph'] == 'Bar':
            dictionary["graph"] = 'Bar'
        else:
            dictionary['graph'] = 'Line'

        dictionary['XAxis'] = xAxis
        dictionary['YAxis'] = yAxis
        self.send(dictionary)

    def send3Data(self):
        """dictionary with 3d datat is created"""
        dictionary = {}
        dictionary['dimension'] = '3D'
        if self.request['structure'] == 'FIGURE1':
            print("1")
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0.5, 0.5, -1]])

            faces = np.hstack([[4, 0, 1, 2, 3],  # square
                [3, 0, 1, 4],  #triangle
                [3, 1, 2, 4],
                [3, 2, 3, 4],
                ])

            vertices = vertices.tolist()
            faces = faces.tolist()

            dictionary["vertices"] = vertices
            dictionary['faces'] = faces

        elif self.request['structure'] == 'FIGURE2':
            print("2")
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0.5, 0.5, -1]])

            faces = np.hstack([[4, 0, 1, 2, 3],  # square
                [3, 0, 1, 4],  #triangle
                [3, 1, 2, 4],
            ])

            vertices = vertices.tolist()
            faces = faces.tolist()

            dictionary["vertices"] = vertices
            dictionary['faces'] = faces

        else:
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0.5, 0.5, -1]])

            faces = np.hstack([[4, 0, 1, 2, 3],  # square
                [3, 0, 1, 4],  #triangle
                [3, 1, 2, 4],
                [3, 2, 3, 4],
                [3, 3, 0, 4]])

            vertices = vertices.tolist()
            faces = faces.tolist()

            dictionary["vertices"] = vertices
            dictionary['faces'] = faces

        self.send(dictionary)

    def send(self, dictionary):
        """requested data is ent back to reciever"""
        block = QByteArray()
        dataStream = QDataStream(block, QIODevice.WriteOnly)
        dataStream.writeUInt16(0)

        data = json.dumps(dictionary)
        dataStream.writeString(data.encode())
        dataStream.device().seek(0)
        dataStream.writeUInt16(block.size() - 2)

        self.clientConnection.write(block)
        self.clientConnection.disconnectFromHost()
        self.clientConnection = None

if __name__ == "__main__":
    """Main function"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())