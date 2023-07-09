#from importlib_metadata import files

from scipy.io.wavfile import write
import os

import csv
import json
import sys
from collections import OrderedDict
import datetime
import shutil
import numpy as np
import pandas as pd
from glob import glob

import time

time.sleep(1) 

from mintsXU4 import mintsLoRaSensing as mSR
from mintsXU4 import mintsDefinitions as mD

from multiprocessing import Pool, freeze_support
from mintsAudio import config as cfg
from mintsAudio import functions as fn

sampleRate         = 44100  # Sample rate
period             = 120    # Duration of recording
channelSelected    = 1
audioFileNamePre   = "mintsAudio"

minConfidence      = .3
numOfThreads       = 4

dataFolder        = mD.dataFolder
tmpFolderName     = mD.dataFolderTmp
jsonFolderName    = mD.dataFolderJson


currentIndex = 0 

def main(cfg):
    labels = pd.read_csv("mintsAudio/labels/labels.csv") 

    while True:
        try:
            audioFolders = glob(tmpFolderName+ "/*/", recursive = True)
            time.sleep(1)
            for folderIn in audioFolders:
                print("-----------------------------")
                print("Looking up folder: " +folderIn)
                freeze_support()
                cfg = fn.configSetUp(cfg,folderIn,minConfidence,numOfThreads)
                soundClassData = pd.read_csv(folderIn + '/'+ audioFileNamePre+  '.BirdNET.results.csv')
                soundClassData["Labels"] = soundClassData["Scientific name"].map(labels.set_index("Scientific name")["Labels"])
                baseDateTime = folderIn.split('/')
                dateTimeBase  = datetime.datetime.strptime(\
                                baseDateTime[-2], '%Y_%m_%d_%H_%M_%S_%f')
                print("Deleting the folder: " +folderIn)
                if os.path.exists(folderIn):
                    shutil.rmtree(folderIn)
                
                for index, row in soundClassData.iterrows():
                    dateTimeCurrent = str(dateTimeBase + datetime.timedelta(seconds = row['Start (s)']))
                    sensorDictionary = OrderedDict([
                        ("label"        ,row['Labels']),
                        ("confidence"   ,row['Confidence'])
                        ])
                    print(sensorDictionary)
                    print(dateTimeCurrent)
                    mSR.directoryCheck(fn.getJsonFileName(jsonFolderName,dateTimeCurrent))
                    with open(fn.getJsonFileName(jsonFolderName,dateTimeCurrent), "w") as outfile:
                        json.dump(sensorDictionary, outfile)
        
        except Exception as e:
            time.sleep(.5)
            print ("Error and type: %s - %s." % (e,type(e)))
            time.sleep(.5)
            print("Audio File Error")
            time.sleep(.5)           

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    main(cfg)    







