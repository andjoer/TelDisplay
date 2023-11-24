import csv
import yaml
import time
# Load YAML configuration
with open('parser_config.yml', 'r') as file:
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


# Function to process each line and return a dictionary of values
def process_line(line):
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
    with open('data.txt', 'r') as infile:
        for line in infile:
            time.sleep(0.2)  # Simulated sampling rate
            if line.startswith('$'):
                row_data = process_line(line)
                if row_data:
                    writer.writerow(row_data)
                
                    outfile.flush()
