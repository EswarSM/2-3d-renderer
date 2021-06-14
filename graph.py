import pyqtgraph as pg

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class MainWindow(QDialog):
    """Window that renders graphs"""
    def __init__(self, graph, xAxis, yAxis):
        super().__init__()
        self.setWindowTitle("GRAPHS")

        self.xAxis= xAxis
        self.yAxis = yAxis
        print(self.xAxis, self.yAxis)

        if graph == 'Bar':
            self.setUpBarGraph()

        else:
            self.setUpPlotter()

    def setUpBarGraph(self):
        """Layout for bargraph"""
        self.plotter = pg.plot()
        label = QLabel("BarGraph")

        barGraph = pg.BarGraphItem(
            x = self.xAxis,
            height = self.yAxis,
            width = 0.3,
            brush = 'r')
        self.plotter.addItem(barGraph)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.plotter)

        self.setLayout(layout)

    def setUpPlotter(self):
        """Layout for linegraph"""
        plotter = pg.plot()
        label = QLabel("Line Graph")

        plotter.plot(
                self.xAxis,
                self.yAxis,
            )

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(plotter)

        self.setLayout(layout)
