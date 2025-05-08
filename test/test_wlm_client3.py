import socket
import time
import json

HOST = '161.122.203.232'  # 서버의 실제 IP 주소 (서버 컴퓨터의 IP)

PORT = 65000          # 서버 포트
CHANNEL = 3           # 이 클라이언트가 요청할 채널 번호 (1번)

# 소켓 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        # 요청 만들기
        request = {
            "device": "wlm",
            "action": "get_wavelength",
            "channel": 3
        }

        # 요청 보내기
        client_socket.send(json.dumps(request).encode())

        # 응답 받기
        response = client_socket.recv(1024)
        data = json.loads(response)

        if 'error' in data:
            print(f"[서버 에러] {data['error']}")
            client_socket.close()
            exit()
        else:
            print(f"Received wavelength: {data}")

        # 2초 대기
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    client_socket.close()