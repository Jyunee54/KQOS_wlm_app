import socket
import json
import time

# 서버 정보
HOST = '161.122.203.232'  # 예: '192.168.0.10'
PORT = 65000          # 서브 서버 포트

# Newport 장비 키 (장비 식별자)
DEVICE_KEY = "6700 SN22500008"

# 소켓 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    # 서버 첫 응답 확인
    response = client_socket.recv(1024)
    data = json.loads(response)

    if 'error' in data:
        print(f"[서버 에러] {data['error']}")
        client_socket.close()
        exit()

    print("[서버 연결 성공]")

    while True:
        print("\nNewport 테스트 메뉴:")
        print("1. 현재 파장 읽기")
        print("2. 파장 설정하기")
        print("3. 종료")
        choice = input("선택 (1/2/3): ")

        if choice == "1":
            # 현재 파장 읽기 요청
            request = {
                "device": "newport",
                "action": "get_wavelength",
                "device_key": DEVICE_KEY
            }
            client_socket.send(json.dumps(request).encode())

        elif choice == "2":
            # 파장 설정 요청
            new_wavelength = input("설정할 파장 (nm) 입력: ")
            request = {
                "device": "newport",
                "action": "set_wavelength",
                "device_key": DEVICE_KEY,
                "value": float(new_wavelength)
            }
            client_socket.send(json.dumps(request).encode())

        elif choice == "3":
            print("클라이언트를 종료합니다.")
            break

        else:
            print("잘못된 입력입니다.")
            continue

        # 서버 응답 받기
        response = client_socket.recv(1024)
        data = json.loads(response)

        if 'error' in data:
            print(f"[서버 에러] {data['error']}")
        else:
            print(f"[서버 응답] {data}")

except Exception as e:
    print(f"[클라이언트 에러] {e}")

finally:
    client_socket.close()
