import csv
import yaml
import time
from gps import nmea_to_dict
# Load YAML configuration

import time

start = time.time()

config_file = 'parser_config.yml'
data_file = 'data.txt'


with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

def get_parameter_names(message_type):
    """Get parameter names and renamed message type based on the configuration."""

    new_name = config[message_type].get("name", message_type)
    params = config[message_type].get("parameters", [])
    return new_name, [f"{param}" for param in params]

# Initialize CSV columns
column_names = ['Time']
known_messages = {}
for message_type in config:
    new_message_type, param_names = get_parameter_names(message_type)
    known_messages[message_type] = param_names
    column_names.extend(param_names)


'''def parse_gps(sentence):

 
    parts = sentence.split(',')

    # Extract latitude and convert it to decimal degrees
    latitude = float(parts[2])
    latitude_degrees = int(latitude / 100)
    latitude_minutes = latitude - latitude_degrees * 100
    latitude_decimal = latitude_degrees + latitude_minutes / 60
    if parts[3] == 'S':
        latitude_decimal *= -1

    # Extract longitude and convert it to decimal degrees
    longitude = float(parts[4])
    longitude_degrees = int(longitude / 100)
    longitude_minutes = longitude - longitude_degrees * 100
    longitude_decimal = longitude_degrees + longitude_minutes / 60
    if parts[5] == 'W':
        longitude_decimal *= -1

    # Extract altitude
    altitude = float(parts[9])

    return latitude_decimal, longitude_decimal, altitude'''


# Function to process each line and return a dictionary of values
def process_line(line):

    if 'GP' in line[:5]: 
        try:
            data = {}
            parsed = nmea_to_dict(line)
            data['Time'] = time.time() - start
            for column_name in column_names:
          
                if column_name in parsed:
                    if parsed[column_name]:
                        data[column_name] = parsed[column_name]
      
            return data
        except Exception as e:
            print(f'Error parsing line: {e}')
            return None
    else: 
        return process_nmea(line)

def process_nmea(line):  # standard NMEA 
    data = dict.fromkeys(column_names, '')  # Initialize all columns with empty strings
    message_part, _ = line.split('*')
    parts = message_part.split(',')
    message_type = parts[0][1:]
    time = parts[1]
    data['Time'] = time
    values = parts[2:]


    if message_type in known_messages:
        for name, value in zip(known_messages[message_type], values):
            data[name] = value

        return data
    else:
        return False
        

# Read NMEA messages and write to CSV
with open('output.csv', 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=column_names)
    writer.writeheader()

    # Continuously read from the input file
    with open(data_file, 'r') as infile:
        for line in infile:
            #time.sleep(0.01)  # Simulated sampling rate
            if line.startswith('$'):
                row_data = process_line(line)
                if row_data:
                    writer.writerow(row_data)
                
                    outfile.flush()
