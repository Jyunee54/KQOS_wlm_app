import socket
import threading
from wlm import *
from newport import newport
from device_config import *
from NewportDevicemanager import NewportDeviceManager
import json


# Define the server host and port
HOST = '0.0.0.0'  # Localhost
# HOST = '192.168.0.7'  # Localhost
PORT = 65000        # Port to listen on (non-privileged ports are > 1023)

# 디버그 모드로 실행 중
wlm = WavelengthMeter(debug=True)
# laser = newport(id = NEWPORT_ID, key = NEWPORT_KEY) # Newport 레이저 초기화

# Newpor 장치 매니저 초기화
device_keys = [NEWPORT_KEY]
newport_manager = NewportDeviceManager(device_keys=device_keys)

newport_lock = threading.Lock()

# 최대 클라이언트 수 제한
MAX_CLIENTS = 2
connected_clients = []
client_lock = threading.Lock()

# WaveLength Meter 제어
def handle_wlm(request):
    try:
        channel = request.get('channel')
        wavelength = wlm.wavelengths[channel]
        return {'wavelength': wavelength}
    except Exception as e:
        return {'error': str(e)}

# Newport 제어
def handle_newport(request):
    try:
        device_key = request.get('device_key')
        action = request.get('action')
        value = request.get('value')

        result_holder = {}

        if newport_lock.acquire(blocking=False):  
            try:
                def perform_action(device):
                    if action == "get_wavelength":
                        result_holder['result'] = device.lbd
                    elif action == "set_wavelength":
                        device.lbd = float(value)
                        result_holder['result'] = f"Wavelength set to {value} nm"
                    else:
                        result_holder['result'] = "Unknown action"
                newport_manager.use_device(device_key, perform_action)
                return result_holder
            finally:
                newport_lock.release()
        else:
            return {"error": "Newport device is busy. Try again later."}

    except Exception as e:
        return {'error': str(e)}

def handle_client(client_socket, address):
    global connected_clients

    with client_lock:
        if len(connected_clients) >= MAX_CLIENTS:
            print(f"Rejected connection from {address}: too many clients")

            # 에러 메시지를 bytes로 변환해서 전송
            error_message = {"error": f"Server busy. Only {MAX_CLIENTS} clients allowed."}
            client_socket.sendall(json.dumps(error_message).encode())
            
            client_socket.close()
            return
        
        connected_clients.append(address)
        print(f"Accepted connection from {address} (current: {len(connected_clients)})")

    # print(f"New connection from {address}")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            request = json.loads(data.decode())
            device_type = request.get('device')

            if device_type == "wlm":
                response = handle_wlm(request)

            elif device_type == "newport":
                # newport 작업은 락을 걸고 처리
                response = handle_newport(request)

            else:
                response = {"error": "Unknown device type"}

            client_socket.send(json.dumps(response).encode())

    except ConnectionResetError:
        print(f"Connection with {address} lost")
    except Exception as e:
        print(f"Error with {address}: {e}")
    finally:
        with client_lock:
            if address in connected_clients:
                connected_clients.remove(address)
        client_socket.close()
        print(f"Connection from {address} closed")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)  # Listen for up to 5 connections
    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            # client_socket = None
            client_socket, client_address = server.accept()
            print(f"Connected by {client_address}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            # client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server.close()
        print("Server stopped.")

if __name__ == "__main__":
    start_server()

