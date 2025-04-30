import socket
import time

HOST = '161.122.203.164'  # 서버의 실제 IP 주소 (서버 컴퓨터의 IP)
PORT = 65000          # 서버 포트
CHANNEL = 2           # 이 클라이언트가 요청할 채널 번호 (1번)

def start_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))  # 서버에 접속
            print(f"Connected to server at {HOST}:{PORT}, requesting channel {CHANNEL}")

            while True:  # 무한 루프로 연결을 계속 유지
                sock.sendall(str(CHANNEL).encode('utf-8'))  # 채널 번호 전송
                data = sock.recv(1024)  # 서버로부터 응답 받기
                print(f"Received wavelength for channel {CHANNEL}: {data.decode('utf-8')} nm")
                time.sleep(2)  # 2초마다 요청 반복

    except Exception as e:
        print(f"Client error: {e}")

if __name__ == "__main__":
    start_client()
