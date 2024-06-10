from pynng import Sub0
import signal
import sys

def receive_and_save(output_file):
    with Sub0(dial='tcp://127.0.0.1:12345', topics=b'') as sub, open(output_file, 'a') as file:
        def signal_handler(sig, frame):
            print('Exiting gracefully')
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            try:
                message = sub.recv().decode()
                print("Received:", message)
                file.write(message + '\n')
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

if __name__ == "__main__":
    output_file = "received.txt"  # Update the path to the output file
    receive_and_save(output_file)
