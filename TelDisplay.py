import sys
import pandas as pd
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QLabel,QLineEdit 
from PyQt5.QtCore import QTimer, pyqtSignal

from PyQt5.QtGui import QPainter
from PyQt5 import QtChart

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PrintWindow(QWidget):
    def __init__(self, axis_data, data_file,main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.start_time_changed.connect(self.update_start_time)
        self.start_time = 0
        self.data_file = data_file
        self.data_columns = []
        self.units = []
        self.df = []
        for (data_column, units) in axis_data:
            if not isinstance(units, list):
                units = [units] * len(data_column)
            else:
                units = self.units
            self.data_columns.extend(data_column)
            self.units.extend(units) 
        self.label_colors = []  # List to store colors for each label
        self.colors = [
                        '#ffb3ba',  # Pastel pink
                        '#ffdfba',  # Pastel orange
                        '#ffffba',  # Pastel yellow
                        '#baffc9',  # Pastel green
                        '#bae1ff',  # Pastel blue
                        '#f2c2e0',  # Pastel purple
                        '#f1cbff',  # Pastel violet
                        '#e7a977',  # Pastel brown
                        '#ffdfdf',  # Light red
                        '#d2f5e3',  # Light mint
                    ]
        self.labels = {}  

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        color_index = 0

        for data_column, unit in zip(self.data_columns, self.units):
            label = QLabel(f"{data_column} ({unit}): ")
            color = self.colors[color_index % len(self.colors)]
            label.setStyleSheet(f"background-color: {color};")  # Set background color
            self.labels[data_column] = label
            self.layout.addWidget(label)
            color_index += 1

        self.setLayout(self.layout)
        self.updateData()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateData)
        self.timer.start(1000)  # Update every second

    def update_start_time(self, start_time):
        # Update logic for new start time
        self.start_time = start_time
        self.updateData(force=True)

    def updateData(self,force=False):
        try:
            df = pd.read_csv(self.data_file)
 
            if (len(df) > len(self.df) or len(self.df) == 0) or force:
                self.df = df.copy()
                df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
                df = df[df['Time'] > self.start_time]
                if len(df) > 0:                             # if we want to save this if its possible due to the try
                    latest_data = df.iloc[-1]
                    # Calculate min and max with NaN values excluded
                    
                    min_data = df.min(skipna=True)
                    max_data = df.max(skipna=True)
                    for data_column, label in self.labels.items():
                        value = latest_data[data_column]
                        min_value = min_data[data_column]
                        max_value = max_data[data_column]
                        unit = self.units[self.data_columns.index(data_column)]
                        label.setText(f"{data_column} ({unit}): Latest: {value}, Min: {min_value}, Max: {max_value}")
        except Exception as e:
            print(f'Error updating data: {e}')

class PlotWindow(QWidget):
    def __init__(self, axis_data, data_file, main_window, dim='2D'):
        super().__init__()

        self.main_window = main_window
        self.main_window.start_time_changed.connect(self.update_start_time)
        self.axis_data = axis_data
        self.start_time = 0
        self.data_file = data_file
        self.dim = dim
        self.labels = {}  
        self.df = []  # something empty that has a length
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        '''if False : #self.dim != '3D':
            self.layout = QVBoxLayout()
            self.chart = QtChart.QChart()
            self.chartView = QtChart.QChartView(self.chart)
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.layout.addWidget(self.chartView)
            self.setLayout(self.layout)
        else:'''
        self.layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure())
        self.layout.addWidget(self.canvas)
        self.data_columns = []
        self.units = []
        for (data_column, units) in self.axis_data:
            if not isinstance(units, list):
                units = [units] * len(data_column)
            else:
                units = self.units
            self.data_columns.extend(data_column)
            self.units.extend(units) 

        for data_column, unit in zip(self.data_columns, self.units):
            label = QLabel(f"{data_column} ({unit}): ")
            self.labels[data_column] = label
            self.layout.addWidget(label)
        
        self.setLayout(self.layout)
        
        self.updatePlot()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(1000)  # Update every second

    def update_start_time(self, start_time):
        # Update logic for new start time
        self.start_time = start_time
        self.updatePlot(force=True)

    def updateLabels(self, df):

        max_data = df.max()
        min_data = df.min()
        latest_data = df.iloc[-1]

        for data_column, label in self.labels.items():
            max_value = max_data[data_column]
            min_value = min_data[data_column]
            value = latest_data[data_column]
            unit = self.units[self.data_columns.index(data_column)]
            label.setText(f"{data_column} ({unit}): {value} max: {max_value} min: {min_value}")

    def updatePlot(self,force=False):
        #try:
            df = pd.read_csv(self.data_file)
            if (len(df) > len(self.df) or len(self.df) == 0) or force:
                self.df = df.copy()
                df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
                df = df[df['Time'] > self.start_time]
                if self.dim == '3D':
                    self.updatePlot3D(df)
                else:
                    self.updatePlot2D(df)
        #except Exception as e:
            #print(f'Error updating plot: {e}')

    def updatePlot3D(self, df):

        ax = self.canvas.figure.add_subplot(111, projection='3d')
        ax.clear()

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Define color list
        color_index = 0

        for i, (params, unit) in enumerate(self.axis_data):
            # Ensure units is a list with correct length
            units = [unit] * len(params) if not isinstance(unit, list) else unit

            # Iterate over parameters in groups of three
            for j in range(0, len(params), 3):
                if j + 2 < len(params):  # Check if there are at least 3 parameters
                    color = colors[color_index % len(colors)]
                    df_subset = df.dropna(subset=[params[j], params[j + 1], params[j + 2]])
                    ax.plot(df_subset[params[j]], df_subset[params[j + 1]], df_subset[params[j + 2]], color=color, label=f"{'-'.join(params[j:j+3])}")
                    color_index += 1

        # Setting labels for the first group of parameters
        if len(self.axis_data) > 0 and len(self.axis_data[0][0]) >= 3:
            first_group_params = self.axis_data[0][0]
            first_group_units = self.axis_data[0][1]
            ax.set_xlabel(f"{first_group_params[0]} ({first_group_units[0]})")
            ax.set_ylabel(f"{first_group_params[1]} ({first_group_units[1]})")
            ax.set_zlabel(f"{first_group_params[2]} ({first_group_units[2]})")

        # Adjusting the axis limits according to the value range
        ax.set_xlim(df[first_group_params[0]].min(), df[first_group_params[0]].max())
        ax.set_ylim(df[first_group_params[1]].min(), df[first_group_params[1]].max())
        ax.set_zlim(df[first_group_params[2]].min(), df[first_group_params[2]].max())

        ax.legend()
        self.canvas.draw()
        self.canvas.draw()

    def updatePlot2D(self, df):
        # Create the subplot once
        if not hasattr(self, 'ax') or self.ax is None:
            self.ax = self.canvas.figure.subplots()

        self.ax.clear()  # Clear the existing plot
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_index = 0

        # Get time range
        time_min = df['Time'].min()
        time_max = df['Time'].max()

        ax_list = [self.ax]  # Keep track of created axes

        for i, (params, unit) in enumerate(self.axis_data):
            ax = ax_list[0] if i == 0 else ax_list[0].twinx()
            ax_list.append(ax)

            for param in params:
                color = colors[color_index % len(colors)]
                subset = df.dropna(subset=['Time', param])
                ax.plot(subset['Time'], subset[param], label=f"{param} ({unit})", color=color)
                color_index += 1

            ax.set_ylabel(f"{', '.join(params)} ({unit})")
            ax.legend(loc='upper left' if i == 0 else 'upper right')

        # Set x-axis limits outside the loop
        self.ax.set_xlim(left=time_min, right=time_max)

        # Redraw the canvas after all plotting
        self.canvas.draw()
        self.updateLabels(df)

    def updatePlot2D_qcharts(self,df):
    
        self.chart.removeAllSeries()
        for data_column, unit in zip(self.data_columns, self.units):
            series = QtChart.QLineSeries()
            for i in range(len(df)):
                series.append(df.iloc[i]['Time'], df.iloc[i][data_column])
            series.setName(f"{data_column} ({unit})")
            self.chart.addSeries(series)
            self.chart.createDefaultAxes()

        

class MainWindow(QMainWindow):
    start_time_changed = pyqtSignal(float)  # Signal to emit when start time changes
    def __init__(self):
        super().__init__()

        self.conf_file = 'display_config.yml'
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

        self.startTimeEdit = QLineEdit(self)
        self.startTimeEdit.setPlaceholderText("Enter Start Time")
        self.layout.addWidget(self.startTimeEdit)

        self.setStartTimeButton = QPushButton("Set Start Time", self)
        self.setStartTimeButton.clicked.connect(self.on_set_start_time_clicked)
        self.layout.addWidget(self.setStartTimeButton)


    def on_set_start_time_clicked(self):
        start_time = self.startTimeEdit.text()
        try:
            start_time = float(start_time)
            self.start_time_changed.emit(start_time)
        except:
            pass

    def openWindow(self, main_point):
        def handleButton():
            if main_point in self.windows and self.windows[main_point].isVisible():
                # Bring the existing window to the front if it's already open
                self.windows[main_point].raise_()
                self.windows[main_point].activateWindow()
            else:
                # Create a new window if it doesn't exist or has been closed
                axis_data = []
                units = []
                dim = '2D'  # Default value for dimension

                window_type = self.config[main_point].get('type', 'plot')  # Extract window type

                if 'axis' in self.config[main_point]:
                    for axis_group in self.config[main_point]['axis']:
                        print(axis_group)
                        for axis, axis_info in axis_group.items():
                            # Extract unit or units
                            unit = axis_info.get('unit', '')
                            if isinstance(unit, list):
                                units.extend(unit)
                            else:
                                units.extend([unit] * len(axis_info['parameters']))

                            params = axis_info.get('parameters', [])

                            # Extract dimension if present
                            if 'dim' in self.config[main_point]:
                                dim = self.config[main_point]['dim']


                        axis_data.append((params,unit))

                if window_type == 'print':
                    window = PrintWindow(axis_data, self.data_file, self)  # Create a print window
                else:
                    window = PlotWindow(axis_data, self.data_file,self, dim=dim)  # Create a plot window

                window.show()

                self.on_set_start_time_clicked()
                self.windows[main_point] = window

        return handleButton

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
