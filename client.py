import sys
import json
import numpy as np

from functools import partial
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QIntValidator
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QLabel,
    QWidget
)

import graph
import objectrender


class MainWindow(QMainWindow):
    """Main window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLIENT")

        self.setUpInitialWindow()

    def setUpInitialWindow(self):
        """
        Initial layout,here you can
        CHOOSE WHAT TYPE OF OBJECT YOU NEED
        """
        # Creating widgets
        self.layout = QGridLayout()
        self.dimensionLabel = QLabel("PICK A DIMENSION")
        self.dimentionComboBox = QComboBox()
        self.button = QPushButton("NEXT")
        self.button.clicked.connect(self.nextPage)

        self.dimentionComboBox.addItem("2D")
        self.dimentionComboBox.addItem("3D")

        # Adding Widgets
        self.layout.addWidget(self.dimensionLabel, 0, 0)
        self.layout.addWidget(self.dimentionComboBox, 0, 1)
        self.layout.addWidget(self.button, 1, 1)

        # Setting layout and widgets
        self.cwidget = QWidget()
        self.setCentralWidget(self.cwidget)
        self.cwidget.setLayout(self.layout)

    def nextPage(self):
        """
        This function executes the layout for 2d/3d objects
        depending upon user's choosing
        """
        data = self.dimentionComboBox.currentText()
        if data == "2D":
            self.twoDimensionalLayout()

        else:
            self.threeDimensionalLayout()

    def twoDimensionalLayout(self):
        """Layout for elements needed for the 2d graph"""
        # Creating widgets
        self.twoDLayout = QGridLayout()
        self.rangeLabel = QLabel("Range:")
        self.pointsLable = QLabel("Number of Points:")
        self.graphLable = QLabel("Select a Graph:")

        self.rangeText = QLineEdit()
        self.rangeText.setValidator(QIntValidator(1, 1000, self))
        self.pointsCombo = QComboBox()
        self.graphType = QComboBox()
        self.backButton = QPushButton("BACK")
        self.nextButton = QPushButton("NEXT")

        self.pointsCombo.addItem('10')
        self.pointsCombo.addItem('20')
        self.pointsCombo.addItem('30')
        self.graphType.addItem('Bar')
        self.graphType.addItem('Line')

        # adding functionality to widgets
        self.backButton.clicked.connect(self.setUpInitialWindow)
        self.nextButton.clicked.connect(self.get2Data)

        # Adding Widgets
        self.twoDLayout.addWidget(self.rangeLabel, 0, 0)
        self.twoDLayout.addWidget(self.pointsLable, 1, 0)
        self.twoDLayout.addWidget(self.graphLable, 2, 0)
        self.twoDLayout.addWidget(self.rangeText, 0, 1)
        self.twoDLayout.addWidget(self.pointsCombo, 1, 1)
        self.twoDLayout.addWidget(self.graphType, 2, 1)
        self.twoDLayout.addWidget(self.backButton, 3, 0)
        self.twoDLayout.addWidget(self.nextButton, 3, 1)

        # Setting layout and widgets
        self.cwidget = QWidget()
        self.setCentralWidget(self.cwidget)
        self.cwidget.setLayout(self.twoDLayout)

    def threeDimensionalLayout(self):
        """Layout for elements needed for the 3d rendering"""
        # Creating widgets
        self.layout = QGridLayout()
        self.objectLabel = QLabel("Select Figure:")
        self.objectCombo = QComboBox()
        self.backButton = QPushButton("BACK")
        self.nextButton = QPushButton("NEXT")

        shapes = ["FIGURE1", "FIGURE2", "FIGURE3"]
        self.objectCombo.addItems(shapes)
        self.backButton.clicked.connect(self.setUpInitialWindow)
        self.nextButton.clicked.connect(self.get3Data)

        # Adding Widgets
        self.layout.addWidget(self.objectLabel, 0, 0)
        self.layout.addWidget(self.objectCombo, 0, 1)
        self.layout.addWidget(self.backButton, 1, 0)
        self.layout.addWidget(self.nextButton, 1, 1)

        # Setting layout and widgets
        self.cwidget = QWidget()
        self.setCentralWidget(self.cwidget)
        self.cwidget.setLayout(self.layout)

    def get2Data(self):
        """getting 2d data by sending request to server for 2d data"""
        limit = self.rangeText.text()
        points = self.pointsCombo.currentText()
        graphType = self.graphType.currentText()

        if limit == '':
            limit = 100
            self.rangeText.setText("100")

        dictionary = {}
        dictionary["dimension"] = '2D'
        dictionary["range"] = limit
        dictionary["points"] = points
        dictionary["graph"] = graphType

        self.setUpSocket()
        self.requestData(dictionary)

    def get3Data(self):
        """getting 3d data by sending request to server for 3d data"""
        structure = self.objectCombo.currentText()

        dictionary = {}
        dictionary["dimension"] = '3D'
        dictionary["structure"] = structure

        self.setUpSocket()
        self.requestData(dictionary)

    def setUpSocket(self):
        """Setting up connection"""
        self.tcpSocket = QTcpSocket()
        self.tcpSocket.readyRead.connect(self.dataIncome)
        # self.tcpSocket.errorOccurred.connect(self.errorDisplay)

        self.nextButton.setEnabled(False)
        self.blockSize = 0
        self.tcpSocket.abort()
        self.tcpSocket.connectToHost("Localhost", 6789)

        return

    def requestData(self, dictionary):
        """sending request data to server"""
        block = QByteArray()
        dataStream = QDataStream(block, QIODevice.WriteOnly)
        dataStream.writeUInt16(0)

        data = json.dumps(dictionary)
        dataStream.writeString(data.encode())
        dataStream.device().seek(0)
        dataStream.writeUInt16(block.size() - 2)

        self.tcpSocket.write(block)

        return

    def dataIncome(self):
        """
        Data from server is recieved and depending
        on dimension either 3d or 3d fiqure widget is openned
        """
        dataStream = QDataStream(self.tcpSocket)

        if self.blockSize == 0:
            if self.tcpSocket.bytesAvailable() < 2:
                return

            self.blockSize = dataStream.readUInt16()

        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return

        self.data = dataStream.readString()
        self.data = json.loads(self.data)

        # enable next button
        self.nextButton.setEnabled(True)

        # print(self.data)

        if self.data['dimension'] == '2D':
            window = graph.MainWindow(
                self.data['graph'],
                self.data['XAxis'],
                self.data['YAxis']
            )
            window.exec()

        elif self.data['dimension'] == '3D':
            print("3D time!")
            vertices = np.array(self.data['vertices'])
            faces = np.array(self.data['faces'])

            print(vertices)
            print(faces)

            self.window = objectrender.Window(vertices, faces)
            self.window.show()


if __name__ == "__main__":
    """Main function"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())