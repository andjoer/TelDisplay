import time
import zmq

def send_file_lines(filename, delay):
    # Create a ZeroMQ context
    context = zmq.Context()
    
    # Create a publisher socket
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://127.0.0.1:12345")
    
    # Open the file and send each line as a message
    with open(filename, 'r') as file:
        for line in file:
            # Strip the newline character and encode the line to bytes
            message = line.strip().encode()
            publisher.send(message)
            time.sleep(delay)
    
    # Close the socket and terminate the context
    publisher.close()
    context.term()

if __name__ == "__main__":
    filename = "gps.dat"  # Update the path to your text file
    delay = 0.004  # Delay in seconds between sending lines
    send_file_lines(filename, delay)
