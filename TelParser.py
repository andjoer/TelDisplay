import csv
import yaml
import time
from gps import nmea_to_dict
# Load YAML configuration

import yaml
import time
import numpy as np

class NMEAParser:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)
        self.column_names = ['Time']
        self.known_messages = self.initialize_known_messages()
        self.start_time = time.time()

    def initialize_known_messages(self):
        known_messages = {}
        for message_type in self.config:
            new_message_type, param_names = self.get_parameter_names(message_type)
            known_messages[message_type] = param_names
            self.column_names.extend(param_names)
        return known_messages

    def get_parameter_names(self, message_type):
        """Get parameter names and renamed message type based on the configuration."""
        new_name = self.config[message_type].get("name", message_type)
        params = self.config[message_type].get("parameters", [])
        return new_name, [f"{param}" for param in params]

    def process_line(self, line):
        if 'GP' in line[:5]:
            try:
                data = {'Time': time.time() - self.start_time}
                parsed = nmea_to_dict(line)

                for column_name in self.column_names:
                    print(column_name)
                    if column_name in parsed and parsed[column_name]:
                        data[column_name] = float(parsed[column_name])
                return data
            except Exception as e:
                print(f'Error parsing line: {e}')
                return None
        else:
            return self.process_nmea(line)

    def process_nmea(self, line):
        data = dict.fromkeys(self.column_names, np.nan)  # Initialize all columns with empty strings
        message_part, _ = line.split('*')
        parts = message_part.split(',')
        message_type = parts[0][1:]
        time = parts[1]
        try:
            data['Time'] = float(time)
        except: 
            data['Time'] = np.nan
        values = parts[2:]

        if message_type in self.known_messages:
            for name, value in zip(self.known_messages[message_type], values):
                try:
                    data[name] = float(value)
                except: 
                    data[name] = np.nan

            return data
        else:
                return False
