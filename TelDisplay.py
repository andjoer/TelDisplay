import sys
import pandas as pd
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QLabel 
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QPainter
from PyQt5 import QtChart

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWindow(QWidget):
    def __init__(self, data_columns, units, data_file, dim='2D'):
        super().__init__()
        self.data_columns = data_columns
        
        self.data_file = data_file
        self.units = units
        self.dim = dim
        self.labels = {}  
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        if self.dim != '3D':
            self.layout = QVBoxLayout()
            self.chart = QtChart.QChart()
            self.chartView = QtChart.QChartView(self.chart)
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.layout.addWidget(self.chartView)
            self.setLayout(self.layout)
        else:
            self.layout = QVBoxLayout()
            self.canvas = FigureCanvas(Figure())
            self.layout.addWidget(self.canvas)
            for data_column, unit in zip(self.data_columns, self.units):
                label = QLabel(f"{data_column} ({unit}): ")
                self.labels[data_column] = label
                self.layout.addWidget(label)
        
            self.setLayout(self.layout)
        
        self.updatePlot()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(1000)  # Update every second
    def updateLabels(self, latest_data,max_data):
        for data_column, label in self.labels.items():
            max_value = max_data[data_column]
            value = latest_data[data_column]
            unit = self.units[self.data_columns.index(data_column)]
            label.setText(f"{data_column} ({unit}): {value} max: {max_value}")

    def updatePlot(self):
        try:
            df = pd.read_csv(self.data_file)
            df.interpolate(inplace=True)  # Interpolate missing values

            if self.dim == '3D':
                self.updatePlot3D(df)
            else:
                self.updatePlot2D(df)
        except Exception as e:
            print(f'Error updating plot: {e}')

    def updatePlot3D(self, df):
        max_values = df.max()
        self.updateLabels(df.iloc[-1],max_values)
        ax = self.canvas.figure.add_subplot(111, projection='3d')
        ax.clear()
        if not isinstance(self.units, list):
            units = [self.units] * len(self.data_columns)
        else:
            units = self.units
        # Plotting the 3D trajectory
        ax.plot(df[self.data_columns[0]], df[self.data_columns[1]], df[self.data_columns[2]])

        # Setting the labels with units
        ax.set_xlabel(f"{self.data_columns[0]} ({units[0]})")
        ax.set_ylabel(f"{self.data_columns[1]} ({units[1]})")
        ax.set_zlabel(f"{self.data_columns[2]} ({units[2]})")

        # Adjusting the axis limits according to the value range
        ax.set_xlim(df[self.data_columns[0]].min(), df[self.data_columns[0]].max())
        ax.set_ylim(df[self.data_columns[1]].min(), df[self.data_columns[1]].max())
        ax.set_zlim(df[self.data_columns[2]].min(), df[self.data_columns[2]].max())

        self.canvas.draw()

    def updatePlot2D(self,df):
    
        df = pd.read_csv('output.csv')

        df.interpolate(inplace=True)  # Interpolate missing values
        self.chart.removeAllSeries()
        for data_column, unit in zip(self.data_columns, self.units):
            series = QtChart.QLineSeries()
            for i in range(len(df)):
                series.append(df.iloc[i]['Time'], df.iloc[i][data_column])
            series.setName(f"{data_column} ({unit})")
            self.chart.addSeries(series)
            self.chart.createDefaultAxes()

        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.conf_file = 'gps_display_config.yml'
        self.data_file = 'output.csv'

        self.initUI()
        
        self.windows = {}

    def initUI(self):
        self.setWindowTitle('Data Visualization')
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        with open(self.conf_file, 'r') as file:
            self.config = yaml.safe_load(file)

        for main_point in self.config.keys():
            btn = QPushButton(main_point, self)
            btn.clicked.connect(self.openWindow(main_point))
            self.layout.addWidget(btn)

    def openWindow(self, main_point):
        def handleButton():
            if main_point in self.windows and self.windows[main_point].isVisible():
                # Bring the existing window to the front if it's already open
                self.windows[main_point].raise_()
                self.windows[main_point].activateWindow()
            else:
                # Create a new window if it doesn't exist or has been closed
                data_columns = []
                units = []
                dim = '2D'  # Default value for dimension

                for axis_dict in self.config[main_point]:  # Iterate over the list of axis dictionaries
                    for axis, axis_info in axis_dict.items():  # Iterate over the dictionary
                        # Extract unit or units
                        unit = axis_info.get('unit', '')
                        if isinstance(unit, list):
                            # If unit is a list, extend units with it
                            units.extend(unit)
                        else:
                            # If unit is a single value, extend units for each parameter
                            units.extend([unit] * len(axis_info['parameters']))

                        data_columns.extend(axis_info['parameters'])  # Collect all parameters
                        
                        # Extract dimension if present
                        if 'dim' in axis_info:
                            dim = axis_info['dim']

                window = PlotWindow(data_columns, units, self.data_file,dim)  # Create a window with all parameters, units, and dimension
                window.show()
                self.windows[main_point] = window

        return handleButton



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
