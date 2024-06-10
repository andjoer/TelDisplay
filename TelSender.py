import time
from pynng import Pub0

def send_file_lines(filename, delay):
    with Pub0(listen='tcp://127.0.0.1:12345') as pub, open(filename, 'r') as file:
        for line in file:
            pub.send(line.strip().encode())
            time.sleep(delay)

if __name__ == "__main__":
    filename = "data.txt"  # Update the path to your text file
    delay = 0.004  # Delay in seconds between sending lines
    send_file_lines(filename, delay)
