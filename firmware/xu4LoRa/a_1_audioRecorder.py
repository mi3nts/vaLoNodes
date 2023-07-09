#from importlib_metadata import files

from scipy.io.wavfile import write
import os

import csv

import sys
from collections import OrderedDict
import datetime

import numpy as np
import pandas as pd

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
tmpFolderName      = mD.dataFolderTmp
minConfidence      = .3
numOfThreads       = 4

dataFolder         = mD.dataFolder

currentIndex = 0 

def main(cfg,currentIndex):
    while True:
        try:

            print("=============")            
            recording = fn.makeAudioFile2(
                        sampleRate,\
                        period,\
                        channelSelected,\
                        tmpFolderName)
            print("=============")
            print()

        except Exception as e:
            time.sleep(.5)
            print ("Error and type: %s - %s." % (e,type(e)))
            time.sleep(.5)
            print("Microphone Not Connected: Check connection")
            time.sleep(.5)
       
if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Connecting to the microphone on Channel: {0}".format(channelSelected) + " with Sample Rate " + str(sampleRate))
    main(cfg,currentIndex)    






