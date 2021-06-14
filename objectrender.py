import pyvista as pv

from PyQt5.QtWidgets import  (
    QFrame,
    QPushButton,
    QVBoxLayout,
    QWidget)
from pyvistaqt import QtInteractor, MainWindow


class Window(MainWindow):
    """Widget to render 3d object"""
    def __init__(self, vertices, faces):
        """layout is created here"""
        super().__init__()

        self.vertices = vertices
        self.faces = faces

        self.setWindowTitle("#D redering")

        self.frame = QFrame()

        self.createRenderer()

    def createRenderer(self):
        """Widgets for 3d renderer creaed here"""
        # creating frame
        self.generalLayout = QVBoxLayout()
        self.cwidget = QWidget()

        self.frame = QFrame()

        # Adding pyvista to interactor object
        self.plotter = QtInteractor(self.frame)
        self.generalLayout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)

        self.structure = pv.PolyData(self.vertices, self.faces)
        self.plotter.add_mesh(self.structure, show_edges=True)
        self.plotter.reset_camera()

        #adding buttons to general layout
        self.button = QPushButton("Show Axes")
        self.generalLayout.addWidget(self.button)
        self.button.clicked.connect(self.showAxis)

        self.setCentralWidget(self.cwidget)
        self.cwidget.setLayout(self.generalLayout)

    def showAxis(self):
        """show axes"""
        self.plotter.show_axes_all()
