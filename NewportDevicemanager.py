import threading
import time
from newport import newport  # Newport 모듈은 이미 임포트되어 있다고 가정

class NewportDeviceManager:
    def __init__(self, device_keys):
        self.device_keys = device_keys  # 여러 장치의 DeviceKey를 리스트로 받음
        self.locks = {key: threading.Lock() for key in device_keys}  # 각 장치에 대해 별도의 Lock 생성
        self.devices = {key: None for key in device_keys}  # 장치 객체를 담을 딕셔너리 (현재는 None으로 초기화)

    def connect_device(self, device_key):
        if device_key in self.device_keys:
            with self.locks[device_key]:  # 장치 사용을 위한 락 획득
                if self.devices[device_key] is None:  # 장치가 이미 연결되지 않았다면
                    try:
                        # Newport 장치 연결 코드 (실제 연결 코드에 맞게 수정 필요)
                        self.devices[device_key] = Newport.newport(id=1, key=device_key)
                        self.devices[device_key].connected = True  # 장치 연결 상태 설정
                        print(f"{device_key} 장치 연결 성공")
                    except Exception as e:
                        print(f"{device_key} 연결 실패: {e}")
                else:
                    print(f"{device_key} 장치는 이미 연결되어 있습니다.")
        else:
            print(f"{device_key}는 지원되지 않는 장치입니다.")

    def disconnect_device(self, device_key):
        if device_key in self.device_keys:
            with self.locks[device_key]:  # 장치 사용을 위한 락 획득
                if self.devices[device_key] is not None:  # 장치가 연결되어 있으면
                    self.devices[device_key].connected = False  # 장치 연결 해제
                    self.devices[device_key] = None
                    print(f"{device_key} 장치 연결 해제")
                else:
                    print(f"{device_key} 장치가 연결되지 않았습니다.")
        else:
            print(f"{device_key}는 지원되지 않는 장치입니다.")

    def use_device(self, device_key, action):
        """장치 사용 함수: 다른 클라이언트가 사용 중이면 대기"""
        if device_key in self.device_keys:
            with self.locks[device_key]:  # 장치 사용을 위한 락 획득
                device = self.devices[device_key]
                if device and device.connected:
                    print(f"{device_key} 장치 사용 시작")
                    action(device)  # 실제 장치에서 원하는 작업 실행
                    print(f"{device_key} 장치 사용 완료")
                else:
                    print(f"{device_key} 장치가 연결되지 않았습니다.")
        else:
            print(f"{device_key}는 지원되지 않는 장치입니다.")


