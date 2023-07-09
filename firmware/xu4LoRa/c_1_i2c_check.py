
# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'

import base64
from cgitb import strong
# import imp
# from this import d
import paho.mqtt.client as mqtt
import datetime 
from datetime import timedelta
import yaml
import collections
import json
import time 
import serial.tools.list_ports
from collections import OrderedDict
from glob import glob
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsPoLo as mPL
from collections import OrderedDict
import struct
import numpy as np
import pynmea2
import shutil

#import SI1132
from mintsI2c.i2c_scd30 import SCD30
from mintsI2c.i2c_as7265x import AS7265X
from mintsI2c.i2c_bme280 import BME280
import math
import sys
import time
import os
import smbus2



debug  = False 

bus     = smbus2.SMBus(0)
scd30   = SCD30(bus,debug)
bme280  = BME280(bus,debug)
as7265x = AS7265X(bus,debug)

loRaE5MiniPorts     = mD.loRaE5MiniPorts
# canareePorts        = mD.canareePorts
# gpsPorts            = mD.gpsPorts
appKey              = mD.appKey
macAddress          = mD.macAddress
jsonFolderName      = mD.dataFolderJson


def getLatitudeCords(latitudeStr,latitudeDirection):
    latitude = float(latitudeStr)
    latitudeCord      =  math.floor(latitude/100) +(latitude - 100*(math.floor(latitude/100)))/60
    if(latitudeDirection=="S"):
        latitudeCord = -1*latitudeCord
    return latitudeCord

def getLongitudeCords(longitudeStr,longitudeDirection):
    longitude = float(longitudeStr)
    longitudeCord      =  math.floor(longitude/100) +(longitude - 100*(math.floor(longitude/100)))/60
    if(longitudeDirection=="W"):
        longitudeCord = -1*longitudeCord
    return longitudeCord        

if __name__ == "__main__":
    
    print()
    print("============ MINTS POLO NODES ============")
    print()

    # I2C Devices 
    scd30Online    = scd30.initiate(30)
    bme280Online   = bme280.initiate(30)
    as7265xOnline  = as7265x.initiate()
    
    joined = True
    print("Hello MINTS")
    while joined:
        start_time = time.time()
        if scd30Online:
            sensorData  =  scd30.read()
            print("SCD30")
            print(sensorData)

        if as7265xOnline:
            print("AS7265X")
            sensorData  =  as7265x.read()
            print(sensorData)
            time.sleep(2)

        if bme280Online:
            print("BME280")
            sensorData  =  bme280.read()
            print(sensorData)
            time.sleep(2)


        time.sleep(6)
        
        
        