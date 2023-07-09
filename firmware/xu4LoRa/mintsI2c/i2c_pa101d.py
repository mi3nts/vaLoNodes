import datetime
from datetime import timedelta
import logging
import smbus2
import struct
import time
import bme280
import math
import time
import pynmea2
from pa1010d import PA1010D

class PAI101D_:

    def __init__(self, i2c_dev,debugIn):
        
        self.gps = PA1010D(debug= debugIn)
        self.gps._i2c = i2c_dev

    def initiate(self):
        try:
            time.sleep(1)

            self.gps.update(timeout=5)

            print("Reading only RMC and GGA Commands")
            self.gps.send_command("PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

            print("Sending to Power Save Mode")
            self.gps.send_command("$PMTK161,0*28")
            time.sleep(1)

            return self.gps.gps_qual is not None;
        except OSError:
            return False
            pass

    def readSentence(self,strExpected, timeOut=2):
        print("Setting PA101D to normal")
        self.gps.send_command("$PMTK225,0*2B")
        timeOut += time.time()
        while time.time() < timeOut:
            try:
                sentence = self.gps.read_sentence()
                print(sentence)
                if sentence.find(strExpected) >0:
                    self.gps.send_command("$PMTK161,0*28")
                    return sentence;                
            except TimeoutError:
                continue
        print("Setting PA101D to low power mode")
        self.gps.send_command("$PMTK161,0*28")
        return;