import sys
import pandas as pd
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QLabel,QLineEdit 
from PyQt5.QtCore import QTimer, pyqtSignal

from PyQt5.QtGui import QPainter
from PyQt5 import QtChart

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from TelConvert import converter
from TelParser import NMEAParser
from PyQt5.QtCore import QThread, pyqtSignal
import time

from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import time
from matplotlib.ticker import MaxNLocator

from pynng import Sub0
import pynng
from pathlib import Path

class FileMonitor(QThread):
    # Define the signal to emit data, specifying the data type as pandas DataFrame
    data_signal = pyqtSignal(pd.DataFrame)

    def __init__(self, filename, parser):
        super().__init__()
        self.filename = filename
        self.running = True
        self.parser = parser
        self.column_names = parser.column_names
        self.buffer = 2
        self.first_line = 0 
        self.address = 'tcp://127.0.0.1:12345'

    def run(self):
        # Initialize the DataFrame with predefined columns.
        df = pd.DataFrame(columns=self.column_names)
        start = time.time()
        try:
         
            print('iteration took', time.time()-start)
            start = time.time()
            check_file = Path(self.filename)
            if check_file.is_file():
                with open(self.filename, 'r') as file:
                    # Read and process all existing lines first
                    
                    for line in file:  # Start counting from 1
                        row_data = self.parser.process_line(line.strip())
                        if row_data:
                            print('row_data')
                            print(row_data)
                            df = pd.concat([df, pd.DataFrame([row_data], columns=self.column_names)])

                # Emit initial data frame if not empty

                self.data_signal.emit(df)

            len_df_old = len(df)
            send_time = time.time()
            with Sub0(dial=self.address, recv_timeout=1000) as sub, open(self.filename, 'a') as file:
                sub.subscribe(b'')  # Subscribe to all topics
                while self.running:
                    try:
                        msg = sub.recv().decode()
                        print('received:', msg)
                        file.write(msg + '\n')
                        row_data = self.parser.process_line(msg.strip())
                        if row_data:
                            print('row_data')
                            print(row_data)
                            df = pd.concat([df, pd.DataFrame([row_data], columns=self.column_names)])
                        #self.data_signal.emit(msg.decode('utf-8'))
                    except pynng.Timeout:
                        continue

                    if time.time()-send_time > 0.1:
                        self.data_signal.emit(df)
                        send_time = time.time()
                        len_df_old = len(df)

                    
                   

                ''' # After processing all lines, move to the end of the file
                file.seek(0, 2)  # Move to the end of the file
                len_start = len(df)
                while self.running:
                    line = file.readline()
                    print('line')
                    print(line)
                    if not line:
                        print('start sleep')
                        time.sleep(0.01)  # Sleep briefly to avoid busy waiting
                        print('stop_sleep')
                        continue
                    row_data = self.parser.process_line(line.strip())
                    if row_data:
                        df = pd.concat([df, pd.DataFrame([row_data], columns=self.column_names)])
                    if len(df) - len_start > self.buffer:
                        self.data_signal.emit(df)
                        len_start = len(df)'''

        except Exception as e:
            print("Error reading from file:", e)

    def stop(self):
        self.running = False



class PrintWindow(QWidget):
    def __init__(self, axis_data, df, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.start_time_changed.connect(self.update_start_time)
        self.start_time = 0
        self.data_columns = []
        self.units = []
        self.df = df
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
        

    def update_start_time(self, start_time):
        # Update logic for new start time
        self.start_time = start_time
        self.handleNewData(self.df)

    def handleNewData(self,df):
        try:
            self.df = df
            df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
            df = df[df['Time'] > self.start_time]
            for col in df.columns:
                if col in converter:
                    df = converter[col](df)

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
    def __init__(self, axis_data, main_window, current_df, dim='2D'):
        super().__init__()
        self.main_window = main_window
        self.main_window.start_time_changed.connect(self.update_start_time)
        self.axis_data = axis_data
        self.start_time = 0
        self.dim = dim
        self.labels = {}  
        self.df = current_df  # Initialize with the provided DataFrame
        self.initUI(current_df)

    def initUI(self, current_df):
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

        if self.dim == '3D':
            self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        else:
            self.ax = self.canvas.figure.subplots()

        self.line_objects = {}
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_index = 0

        for i, (params, units) in enumerate(self.axis_data):
            ax = self.ax if self.dim == '3D' else (self.ax if i == 0 else self.ax.twinx())
            for param in params:
                color = colors[color_index % len(colors)]
                line, = ax.plot([], [], label=f"{param} ({units})", color=color)
                self.line_objects[param] = line
                label = QLabel(f"{param} ({units}): ")
                self.labels[param] = label
                self.layout.addWidget(label)
                color_index += 1

            ax.set_ylabel(f"{', '.join(params)} ({units})")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
            ax.legend()

        self.setLayout(self.layout)
        self.handleNewData(self.df)

    def update_start_time(self, start_time):
        self.start_time = start_time
        self.handleNewData(self.df)

    def updateLabels(self, df):
        min_data = df.min(skipna=True)
        max_data = df.max(skipna=True)
        latest_data = df.iloc[-1] if not df.empty else pd.Series()

        for data_column, label in self.labels.items():
            if data_column in df.columns:
                value = latest_data[data_column]
                min_value = min_data[data_column]
                max_value = max_data[data_column]
                label.setText(f"{data_column} ({self.units[self.data_columns.index(data_column)]}): Latest: {value}, Min: {min_value}, Max: {max_value}")

    def handleNewData(self, df):
        start = time.time()
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df = df[df['Time'] > self.start_time]
        if self.dim == '3D':
            self.updatePlot3D(df)
        else:
            self.updatePlot2D(df)
        self.updateLabels(df)

        print('update took', time.time()-start)

    def updatePlot3D(self, df):
        self.ax.clear()
        color_index = 0
        for i, (params, units) in enumerate(self.axis_data):
            for j in range(0, len(params), 3):
                if j + 2 < len(params):
                    color = self.colors[color_index % len(self.colors)]
                    df_subset = df.dropna(subset=params[j:j+3])
                    self.ax.plot3D(df_subset[params[j]], df_subset[params[j + 1]], df_subset[params[j + 2]], color=color)
                    color_index += 1
        self.ax.legend()
        self.canvas.draw()

    def updatePlot2D(self, df):
        # Keep track of axes that need to be updated
        axes_to_update = set()

        # Update data for each line and record which axes they belong to
        for param, line in self.line_objects.items():
            if param in df.columns:
                subset = df.dropna(subset=['Time', param])
                line.set_data(subset['Time'], subset[param])
                axes_to_update.add(line.axes)  # Collect the axes to update

        # Recompute and rescale each axis that has been updated
        for ax in axes_to_update:
            ax.relim()  # Recompute the data limits for the current axis
            ax.autoscale_view()  # Adjust the view limits to the new data limits

        self.canvas.draw()  # Redraw the plot with updated axes

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
        self.data_file = 'received.txt'

        
        self.parser = NMEAParser('parser_config.yml')
        self.current_df = pd.DataFrame(columns=self.parser.column_names)
        self.file_monitor = FileMonitor(self.data_file, self.parser)
        self.file_monitor.data_signal.connect(self.handleNewData)
        self.file_monitor.start()  # Start the monitoring thread
        
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


    def handleNewData(self, new_df):
        self.current_df = new_df
        # Emit data to all open windows
        for window in self.windows.values():
            if isinstance(window, PrintWindow) or isinstance(window, PlotWindow):
                print('handle new data')
                window.handleNewData(new_df)

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
                    window = PrintWindow(axis_data, self,self.current_df)  # Create a print window
                else:
                    window = PlotWindow(axis_data ,self, self.current_df, dim=dim)  # Create a plot window

                window.show()

                self.on_set_start_time_clicked()
                self.windows[main_point] = window

        return handleButton

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
