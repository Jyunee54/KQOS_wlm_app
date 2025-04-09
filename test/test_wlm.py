import unittest
from wlm import WavelengthMeter
import time

class Test(unittest.TestCase):
    
    def test(self):
        wlm = WavelengthMeter()
        print(wlm)
        while True :    
            for i in [0,1,2]:
                print("Wavelength at channel %d:\t%.6f nm" % (i, wlm.wavelengths[i]))
            time.sleep(0.5)