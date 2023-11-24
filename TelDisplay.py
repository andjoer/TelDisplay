import sys
import pandas as pd
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWindow(QWidget):
    def __init__(self, data_columns, units):
        super().__init__()
        self.data_columns = data_columns
        self.units = units  # List of units
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure())
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.ax = self.canvas.figure.subplots()
        self.updatePlot()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(100)

    def updatePlot(self):
        try:
            df = pd.read_csv('output.csv')
            print(df.head())
            df.interpolate(inplace=True)  # Interpolate missing values
            self.ax.clear()
            for data_column, unit in zip(self.data_columns, self.units):
                self.ax.plot(df['Time'], df[data_column], label=f"{data_column} ({unit})")
            self.ax.legend()
            self.ax.figure.canvas.draw()
        except:
            print('waiting for file')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.windows = {}

    def initUI(self):
        self.setWindowTitle('Data Visualization')
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        with open('display_config.yml', 'r') as file:
            self.config = yaml.safe_load(file)

        for main_point in self.config.keys():
            btn = QPushButton(main_point, self)
            btn.clicked.connect(self.openWindow(main_point))
            self.layout.addWidget(btn)

    def openWindow(self, main_point):
        def handleButton():
            # Check if the window exists and is visible
            if main_point in self.windows and self.windows[main_point].isVisible():
                # Bring the existing window to the front if it's already open
                self.windows[main_point].raise_()
                self.windows[main_point].activateWindow()
            else:
                # Create a new window if it doesn't exist or has been closed
                data_columns = []
                units = []
                for axis_dict in self.config[main_point]:  # Iterate over the list of axis dictionaries
                    for axis, axis_info in axis_dict.items():  # Iterate over the dictionary
                        unit = axis_info.get('unit', '')  # Extract the unit
                        data_columns.extend(axis_info['parameters'])  # Collect all parameters
                        units.extend([unit] * len(axis_info['parameters']))  # Collect units for each parameter
                window = PlotWindow(data_columns, units)  # Create a window with all parameters and units
                window.show()
                self.windows[main_point] = window

        return handleButton


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
