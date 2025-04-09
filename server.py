import socket
import threading
from wlm import *


# Define the server host and port
HOST = '0.0.0.0'  # Localhost
# HOST = '192.168.0.7'  # Localhost
PORT = 65000        # Port to listen on (non-privileged ports are > 1023)


wlm = WavelengthMeter(debug=True)

# 최대 클라이언트 수 제한
MAX_CLIENTS = 2
connected_clients = []
client_lock = threading.Lock()

def handle_client(client_socket, address):
    global connected_clients

    with client_lock:
        if len(connected_clients) >= MAX_CLIENTS:
            print(f"Rejected connection from {address}: too many clients")
            client_socket.sendall(f"Server busy. Only {MAX_CLIENTS} clients allowed.")
            client_socket.close()
            return
        
        connected_clients.append(address)
        print(f"Accepted connection from {address} (current: {len(connected_clients)})")

    # print(f"New connection from {address}")
    try:
        while True:
            # Receive data from the client
            message = client_socket.recv(1024)
            if not message:
                # Connection closed by the client
                break
            print(f"Received from {address}: {message.decode('utf-8')}")
        
            # message_in_int = int(message.decode('utf-8'))
            # i = message_in_int
            # print("Wavelength at channel %d:\t%.6f nm" % (i, wlm.wavelengths[i]))

            channel = int(message.decode('utf-8'))
            wavelength = wlm.wavelengths[channel]
            print(f"Wavelength at channel {channel}: {wavelength:.6f} nm")
            
            # get wavelength meter value by channel
            client_socket.sendall(str(wlm.wavelengths[i]).encode('utf-8'))
            
    except ConnectionResetError:
        print(f"Connection with {address} lost")
    except KeyboardInterrupt:
        print('Exit by Keyboard Interrupt')
        exit()
    finally:
        with client_lock:
            if address in connected_clients:
                connected_clients.remove(address)
        client_socket.close()
        print(f"Connection from {address} closed")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)  # Listen for up to 5 connections
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket = None
        try :
            client_socket, client_address = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except KeyboardInterrupt:
            if client_socket: 
                client_socket.close()
            break  

if __name__ == "__main__":
    start_server()
