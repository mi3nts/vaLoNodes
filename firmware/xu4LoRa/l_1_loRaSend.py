
# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'
import itertools
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
from mintsI2c.i2c_bme280   import BME280
from mintsI2c.i2c_scd30    import SCD30
from mintsI2c.i2c_as7265x  import AS7265X
from mintsI2c.i2c_pa101d   import PAI101D_


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
pa101d  = PAI101D_(bus,debug)


loRaE5MiniPorts     = mD.loRaE5MiniPorts
ips7100Ports        = mD.ips7100Ports
rainPorts           = mD.rainPorts 

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

def mintsBCConcatSend08(serE5MiniIn):
    sensorData =  list(itertools.repeat (0,8*3+1))
    print(len(sensorData))
    jsonFiles = sorted(glob(jsonFolderName+ "/*.json", recursive = True))
    
    if len(jsonFiles)<=0:
      print("No Sound data")
      return
    currentFiles= 0
    maxFiles = 8
    
    for idx, fileIn in enumerate(jsonFiles):
        if(currentFiles>=maxFiles):
            print("Too Many JSON files")
            break
        print("================================")
        print("Looking up file: " + fileIn +" with index:" + str(idx)) 
        baseDateTime = fileIn.replace("_mintsAudio.json","").split('/')
        duration     = datetime.datetime.now() - datetime.datetime.strptime(\
                            baseDateTime[-1], '%Y_%m_%d_%H_%M_%S_%f')
        durSeconds = int(duration.total_seconds())
            
        if durSeconds < 65534:
            with open(fileIn, 'r') as f:
                jsonData = json.load(f)
            print(idx*3)
            sensorData[idx*3+1] = durSeconds
            sensorData[idx*3+2] = jsonData['label']
            sensorData[idx*3+3] = jsonData['confidence']
  
            
        if os.path.isfile(fileIn):
            print("Deleting file: " +fileIn)
            os.remove(fileIn)
            currentFiles= currentFiles+1
            
    if currentFiles>0:
        sensorData[0] = currentFiles
        print("Sensor Data")
        print(sensorData)
        mPL.readSensorDataBirdSong(sensorData,"MBCLR002",serE5MiniIn)
        
  
def mintsBCSend(serE5MiniIn,numOfFiles):
    jsonFiles = sorted(glob(jsonFolderName+ "/*.json", recursive = True))
    currentFiles= 0
    for idx, fileIn in enumerate(jsonFiles):
        if(currentFiles>=numOfFiles):
            print("Too Many JSON files")
            break
        print("-======================================================================-")
        print("Looking up file: " + fileIn +" with index:" + str(idx)) 
        baseDateTime = fileIn.replace("_mintsAudio.json","").split('/')
        duration     = datetime.datetime.now() - datetime.datetime.strptime(\
                            baseDateTime[-1], '%Y_%m_%d_%H_%M_%S_%f')
        durSeconds = int(duration.total_seconds())
            
        if durSeconds < 65534:
            with open(fileIn, 'r') as f:
                jsonData = json.load(f)
            
            sensorData = [durSeconds,jsonData['label'],jsonData['confidence']]
            print(sensorData)
            mPL.readSensorDataBirdSong(sensorData,"MBCLR001",serE5MiniIn)
          	
        if os.path.isfile(fileIn):
            print("Deleting file: " +fileIn)
            os.remove(fileIn)
            currentFiles= currentFiles+1
  


if __name__ == "__main__":
    
    print()
    print("============ MINTS POLO NODES ============")
    print()
    mPL.readingDeviceProperties(macAddress,loRaE5MiniPorts,ips7100Ports,[])
    
    print("")
    e5MiniOnline,serE5Mini   = mPL.getPort(loRaE5MiniPorts,0,9600)
    ips7100Online,serIPS7100 = mPL.getPort(ips7100Ports,0,115200)
    rainOnline,serRain       = mPL.getRG15Port(rainPorts,0,9600)
    
    # I2C Devices 
    scd30Online    =  scd30.initiate(30)
    bme280Online   =  bme280.initiate(30)
    as7265xOnline  =  as7265x.initiate()
    pa101dOnline   =  pa101d.initiate()
    mbls001Onlune  =  mbls001.initiate()
    
    while not mPL.loRaE5MiniJoin(e5MiniOnline,serE5Mini):
      print("Trying to connect")
      time.sleep(5)
    
    while True:
        try:    
            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataI2c(bme280Online,bme280,"BME280V2",serE5Mini)
            
            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataI2c(scd30Online,scd30,"SCD30",serE5Mini)
            
            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataGPSI2C(pa101dOnline,pa101d,"GPGGAPL",serE5Mini)

            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataI2c(as7265xOnline,as7265x,"AS7265X",serE5Mini)
    
            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataRG15(rainOnline,serRain,"RG15",serE5Mini)

            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataI2c(mbls001Onlune,mbls001,"MBLS001",serE5Mini)

            mPL.readSensorData(ips7100Online,serIPS7100,"IPS7100",serE5Mini)
            mintsBCConcatSend08(serE5Mini)
            mPL.readSensorDataGPSI2C(pa101dOnline,pa101d,"GPRMCPL",serE5Mini)

        except Exception as e:
            time.sleep(.5)
            print ("Error and type: %s - %s." % (e,type(e)))
            time.sleep(.5)
            print("Data Packet Not Sent")
            time.sleep(.5)

                  
        
        
        

        
        
        
        
        