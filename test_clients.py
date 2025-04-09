# test_clients.py
import socket
import threading
import time

HOST = '161.122.203.94'  # 서버 주소
# HOST = '192.168.0.7'  # 서버 주소
PORT = 65000          # 서버 포트

def client_thread(name, channel):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            print(f"[{name}] Connected to server.")

            # 채널 번호 전송
            for _ in range(5):
                sock.sendall(str(channel).encode('utf-8'))
                data = sock.recv(1024)
                print(f"[{name}] Received wavelength for channel {channel}: {data.decode('utf-8')} nm")
                time.sleep(2)

    except Exception as e:
        print(f"[{name}] Error: {e}")

# 두 개의 클라이언트 스레드 실행
if __name__ == "__main__":
    t1 = threading.Thread(target=client_thread, args=("Client-1", 1))
    t2 = threading.Thread(target=client_thread, args=("Client-2", 2))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Test complete.")
