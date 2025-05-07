# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 17:33:35 2022

@author: user
"""
# https://github.com/marvync/Laser-automation-NewFocus : basic sample
# https://github.com/gregmoille/InstrumentControl/blob/master/pyLaser/newfocus.py   -> to JeongHo lee,  this has more functionality.  - Kang. please implement these functions.


# Newport Tunable Laser를 제어하기 위한 Python 클래스
# .NET 기반의 DLL(UsbDllWrap.dll)을 이용해 하드웨어 제어 수행
# Newport의 USB 인터페이스를 통해 파장, 출력, 스캔 속도 등을 설정하거나 질의

import os
import sys
# import ipdb
import numpy as np
import time
# import clr
from datetime import datetime
import pyvisa
# import matplotlib.pyplot as plt
from time import sleep
import logging

# from clr import System
# from System.Text import StringBuilder
# from System import Int32
# from System.Reflection import Assembly

# from wlm import WavelengthMeter
sys.path.append(
    "C:\\Program Files\\New Focus\\New Focus Tunable Laser Application\\Bin"
)
# clr.AddReference("UsbDllWrap")
# import Newport

ProductID = 4106
DeviceKey = "6700 SN22500008"

# Newport 장치와의 실제 통신 핸들
class newport:
    """def __init__(self ,ProductID, DeviceKey):
    self.ProductID = ProductID
    self._DeviceKey = DeviceKey
    self.tlb = Newport.USBComm.USB()
    self.answer = StringBuilder(64)
    self.tlb.OpenDevices(self.ProductID, True)
    wlmeter = WavelengthMeter()"""

    def __init__(self, id = int, key = str, debug = False):
        super(newport, self).__init__()
        self.debug = debug          # 디버그 모드

        try:
            self._dev = Newport.USBComm.USB()   # Neport 장치와의 실제 통신 핸들
        except Exception as err:
            print(err)
            self._dev = None
            self.debug = True
        
        if not self.debug:
            from System.Text import StringBuilder
            self.answer = StringBuilder(64)
            self._buff = StringBuilder(64)
        else:
            self.answer = ""
            self._buff = ""

        # Laser state
        self._open = False
        self._DeviceKey = key               # 장치 고유 식별자
        self._idLaser = id                  # 장치 고유 식별자
        # self.answer = StringBuilder(64)
        self.Device_config = "newport"
        # Laser properties
        self._lbd = "0"                     # 레이저 제어 관련 내부 변수
        self._cc = 0        
        self._scan_lim = []
        self._scan_speed = 0
        self._scan = 0
        self._beep = 0
        self._output = 0                    # 레이저 제어 관련 내부 변수
        self._is_scaning = False
        # self._is_changing_lbd = False
        self._no_error = '0,"NO ERROR"'
        self._haserr = False
        # Miscs
        # self._buff = StringBuilder(64)
        self._err_msg = ""
        self.connected = True

    # -- Decorators --
    # ---------------------------------------------------------
    def Checkopen(fun):
        def wrapper(*args, **kwargs):
            self = args[0]
            # if self._open and self._DeviceKey:
            if self._open and self._DeviceKey:
                out = fun(*args, **kwargs)
                return out
            else:
                pass

        return wrapper

    # -- Methods --
    # --------------------------------------------------------
    def get_device_info(self):
        return self.Device_config

    def set_piezo_voltage(self, pzt_value):
        self.pzt = pzt_value

    def get_piezo_voltage(self):
        return self.pzt

    def set_wavelength(self, lbd_value):
        self.lbd_value = lbd_value

    def Query(self, word):
        if self.debug or self._dev is None:
            # 디버그 모드용 가짜 응답
            fake_responses = {
                "SENSe:WAVElength?": "1550.123",
                "OUTPut:STATe?": "1",
                "SOUR:VOLT:PIEZ?": "50.0",
                "*IDN?": "DEBUG-NEWPORT",
                "*STB?": "0",
                "ERRSTR?": "0,\"NO ERROR\""
            }
            response = fake_responses.get(word.strip(), "MOCK_RESPONSE")
            print(f"[DEBUG][Query] {word.strip()} -> {response}")
            return response
        else:
            self._buff.Clear()
            self._dev.Query(self._DeviceKey, word, self._buff)
            # print(self._DeviceKey, word , self._buff)
            return self._buff.ToString()

    # -- Properties --
    # ---------------------------------------------------------
    @property
    # @InOut.output(bool)
    def connected(self):
        return self._open

    @connected.setter
    # @Catch.error
    def connected(self, value):     # 자동 연결(장치 연결을 시도하고, 버퍼를 비우며 초기 상태 확인 후 연결 완료 여부 출력)
        if value:
            if self.debug:
                print(f"[DEBUG] 디바이스 없이 연결된 것으로 간주합니다.")
                self._open = True
                return  # 💥 실제 연결 로직 실행하지 않음
            if self._DeviceKey:
                # try:
                out = self._dev.OpenDevices(self._idLaser, True)
                tab = self._dev.GetDeviceTable()
                # empty buffer
                out = self._dev.Read(self._DeviceKey, self._buff)
                # ipdb.set_trace()
                while not (out == -1 or out == -2 or out == int("-2")):
                    out = self._dev.Read(self._DeviceKey, self._buff)
                    print("Empyting the buffer: {}".format(out))
                    time.sleep(0.5)
                idn = self.identity
                if not idn == "":
                    print("\nLaser connected: {}".format(idn))
                else:
                    logging.warning("The newport doesn't connected")
                    self._dev.CloseDevices()
                    time.sleep(0.2)

                # ipdb.set_trace()
                self.error
                self._open = True
                # except Exception as e:
                #     print(e)

        else:
            self._dev.CloseDevices()
            self._open = False

    @property
    # @InOut.output(bool)
    def output(self):
        word = "OUTPut:STATe?"
        self._output = self.Query(word)
        return self._output

    @output.setter
    # @Catch.error
    # @InOut.accepts(bool)
    def output(self, value):
        word = "OUTPut:STATe {}".format(int(value))
        self.Query(word)
        self._output = value

    @property
    # @InOut.output(float)
    def lbd(self):
        word = "SENSe:WAVElength?"
        self._lbd = self.Query(word)
        if self.debug:
            print("[DEBUG] read wavelength")
        else:
            print("read wavelength")
        # print(self._lbd)
        return self._lbd

    @property
    # @InOut.output(float)
    def pzt(self):
        word = "SOUR:VOLT:PIEZ?"
        self._pzt = self.Query(word)
        return self._pzt

    @pzt.setter
    # @Catch.error
    # @InOut.accepts(float)
    def pzt(self, value):
        word = "SOUR:VOLT:PIEZ {}".format(value)
        self.Query(word)
        self._pzt = value

    @lbd.setter
    # @InOut.accepts(float)
    # @Catch.error
    def lbd(self, value):
        self._targetlbd = value
        self.Query("OUTP:TRACK 1")
        word = "SOURCE:WAVE {}".format(value)
        self.Query(word)
        if self.debug:
            print(f"[DEBUG] write wavelength {value}")
        else:
            print(f"write wavelength {value}")
        self._lbd = value

    @property
    # @InOut.output(float,float)
    def scan_limit(self):
        word1 = "SOUR:WAVE:START?"
        word2 = "SOUR:WAVE:STOP?"
        self._scan_lim = [self.Query(word1), self.Query(word2)]
        return self._scan_lim

    @scan_limit.setter
    # @Catch.error
    # @InOut.accepts(list)
    def scan_limit(self, value):
        start = value[0]
        stop = value[1]
        word1 = "SOUR:WAVE:START {}".format(start)
        self.Query(word1)
        word2 = "SOUR:WAVE:STOP {}".format(stop)
        self.Query(word2)
        self._scan_lim = value

    @property
    # @Catch.error
    # @InOut.output(float)
    def scan_speed(self):
        word1 = "SOUR:WAVE:SLEW:FORW?"
        self._scan_speed = self.Query(word1)
        return self._scan_speed

    @scan_speed.setter
    # @Catch.error
    # @InOut.accepts(float)
    def scan_speed(self, value):
        word = "SOUR:WAVE:SLEW:FORW {}".format(value)
        self.Query(word)
        word = "SOUR:WAVE:SLEW:RET {}".format(0.1)
        self.Query(word)
        self._scan_speed = value

    @property
    # @InOut.output(float)
    def scan(self):
        word = "SOUR:WAVE:DESSCANS?"
        self._scan = self.Query(word)
        return self._scan

    @scan.setter
    # @Catch.error
    # @ChangeState.scan("OUTPut:SCAN:START",'OUTPut:SCAN:STOP')
    # @InOut.accepts(bool)
    def scan(self, value):
        self.Query("SOUR:WAVE:DESSCANS 1")
        self._scan = value
        if self._scan:
            self.Query("OUTPut:SCAN:START")
        else:
            self.Query("OUTPut:SCAN:STOP")

    @property
    # @InOut.output(bool)
    def beep(self):
        word = "BEEP?"
        self._beep = self.Query(word)
        return self.beep

    @beep.setter
    # @Catch.error
    # @InOut.accepts(bool)
    def beep(self, value):
        word = "BEEP ".format(int(value))
        self.Query(word)
        self._beep = value

    @property
    def identity(self):
        word = "*IDN?"
        self._id = self.Query(word)
        return self._id

    @property
    def error(self):
        word = "ERRSTR?"
        self._error = ""
        err = self.Query(word)
        return err

    @property
    def has_error(self):
        word = "*STB?"
        dum = self.Query(word)
        if dum == "128":
            self._haserr = True
        if dum == "0":
            self._haserr = False
        return self._haserr

    @property
    # @InOut.output(bool)
    def _is_changing_lbd(self):
        return self.Query("OUTP:TRACK?")

    @property
    def clear(self):
        pass

    @clear.setter
    # @InOut.accepts(bool)
    def clear(self, val):
        if val:
            self.Query("*CLS")