import socket
from threading import Thread

# Define the server host and port to connect to
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        while True:
            # Read user input
            # message = input("Enter message to send (or 'exit' to quit): ")
            message = "WAVELENGTH "
            if message.lower() == 'exit':
                print("Closing connection.")
                break

            # Send message to the server
            client_socket.sendall(message.encode('utf-8'))

            # Receive the echoed message from the server
            response = client_socket.recv(1024)
            print(f"Received from server: {response.decode('utf-8')}")






if __name__ == "__main__":
    thread1 = Thread( target=start_client, args=() )
    thread1.start()

    thread1.join()

