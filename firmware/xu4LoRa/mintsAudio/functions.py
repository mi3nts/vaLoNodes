import os

import json
import operator

import datetime
import traceback

from scipy.io.wavfile import write

import argparse
import sounddevice as sd

from multiprocessing import Pool, freeze_support

import sys
import numpy as np

# import config as cfg
from mintsAudio import config as cfg

from mintsAudio import audio
from mintsAudio import model
from mintsXU4 import mintsLoRaSensing as mSR


def clearErrorLog():

    if os.path.isfile(cfg.ERROR_LOG_FILE):
        os.remove(cfg.ERROR_LOG_FILE)

def writeErrorLog(msg):

    with open(cfg.ERROR_LOG_FILE, 'a') as elog:
        elog.write(msg + '\n')

def parseInputFiles(path, allowed_filetypes=['wav', 'flac', 'mp3', 'ogg', 'm4a']):

    # Add backslash to path if not present
    if not path.endswith(os.sep):
        path += os.sep

    # Get all files in directory with os.walk
    files = []
    for root, dirs, flist in os.walk(path):
        for f in flist:
            if len(f.rsplit('.', 1)) > 1 and f.rsplit('.', 1)[1].lower() in allowed_filetypes:
                files.append(os.path.join(root, f))

    print('Found {} files to analyze'.format(len(files)))

    return sorted(files)

def loadCodes():

    with open(cfg.CODES_FILE, 'r') as cfile:
        codes = json.load(cfile)

    return codes

def loadLabels(labels_file):
#  encoding="utf-8"
    labels = []
  # Added on Friday June 24 
    with open(labels_file, 'r', encoding="utf-8") as lfile:
        for line in lfile.readlines():
            labels.append(line.replace('\n', ''))    

    return labels

def loadSpeciesList(fpath):

    slist = []
    if not fpath == None:
        with open(fpath, 'r') as sfile:
            for line in sfile.readlines():
                species = line.replace('\r', '').replace('\n', '')
                slist.append(species)

    return slist

def predictSpeciesList():

    l_filter = model.explore(cfg.LATITUDE, cfg.LONGITUDE, cfg.WEEK)
    cfg.SPECIES_LIST_FILE = None
    cfg.SPECIES_LIST = []
    for s in l_filter:
        if s[0] >= cfg.LOCATION_FILTER_THRESHOLD:
            cfg.SPECIES_LIST.append(s[1])

def saveResultFile(r, path, afile_path):

    # Make folder if it doesn't exist
    if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # Selection table
    out_string = ''

    if cfg.RESULT_TYPE == 'table':

        # Raven selection header
        header = 'Selection\tView\tChannel\tBegin Time (s)\tEnd Time (s)\tLow Freq (Hz)\tHigh Freq (Hz)\tSpecies Code\tCommon Name\tConfidence\n'
        selection_id = 0

        # Write header
        out_string += header
        
        # Extract valid predictions for every timestamp
        for timestamp in getSortedTimestamps(r):
            rstring = ''
            start, end = timestamp.split('-')
            for c in r[timestamp]:
                if c[1] > cfg.MIN_CONFIDENCE and c[0] in cfg.CODES and (c[0] in cfg.SPECIES_LIST or len(cfg.SPECIES_LIST) == 0):
                    selection_id += 1
                    label = cfg.TRANSLATED_LABELS[cfg.LABELS.index(c[0])]
                    rstring += '{}\tSpectrogram 1\t1\t{}\t{}\t{}\t{}\t{}\t{}\t{:.4f}\n'.format(
                        selection_id, 
                        start, 
                        end, 
                        150, 
                        12000, 
                        cfg.CODES[c[0]], 
                        label.split('_')[1], 
                        c[1])

            # Write result string to file
            if len(rstring) > 0:
                out_string += rstring

    elif cfg.RESULT_TYPE == 'audacity':

        # Audacity timeline labels
        for timestamp in getSortedTimestamps(r):
            rstring = ''
            for c in r[timestamp]:
                if c[1] > cfg.MIN_CONFIDENCE and c[0] in cfg.CODES and (c[0] in cfg.SPECIES_LIST or len(cfg.SPECIES_LIST) == 0):
                    label = cfg.TRANSLATED_LABELS[cfg.LABELS.index(c[0])]
                    rstring += '{}\t{}\t{:.4f}\n'.format(
                        timestamp.replace('-', '\t'), 
                        label.replace('_', ', '), 
                        c[1])

            # Write result string to file
            if len(rstring) > 0:
                out_string += rstring

    elif cfg.RESULT_TYPE == 'r':

        # Output format for R
        header = 'filepath,start,end,scientific_name,common_name,confidence,lat,lon,week,overlap,sensitivity,min_conf,species_list,model'
        out_string += header

        for timestamp in getSortedTimestamps(r):
            rstring = ''
            start, end = timestamp.split('-')
            for c in r[timestamp]:
                if c[1] > cfg.MIN_CONFIDENCE and c[0] in cfg.CODES and (c[0] in cfg.SPECIES_LIST or len(cfg.SPECIES_LIST) == 0):                    
                    label = cfg.TRANSLATED_LABELS[cfg.LABELS.index(c[0])]
                    rstring += '\n{},{},{},{},{},{:.4f},{:.4f},{:.4f},{},{},{},{},{},{}'.format(
                        afile_path,
                        start,
                        end,
                        label.split('_')[0],
                        label.split('_')[1],
                        c[1],
                        cfg.LATITUDE,
                        cfg.LONGITUDE,
                        cfg.WEEK,
                        cfg.SIG_OVERLAP,
                        (1.0 - cfg.SIGMOID_SENSITIVITY) + 1.0,
                        cfg.MIN_CONFIDENCE,
                        cfg.SPECIES_LIST_FILE,
                        os.path.basename(cfg.MODEL_PATH)
                    )
            # Write result string to file
            if len(rstring) > 0:
                out_string += rstring

    else:

        # CSV output file
        header = 'Start (s),End (s),Scientific name,Common name,Confidence\n'

        # Write header
        out_string += header

        for timestamp in getSortedTimestamps(r):
            rstring = ''
            for c in r[timestamp]:                
                start, end = timestamp.split('-')
                if c[1] > cfg.MIN_CONFIDENCE and c[0] in cfg.CODES and (c[0] in cfg.SPECIES_LIST or len(cfg.SPECIES_LIST) == 0):
                    label = cfg.TRANSLATED_LABELS[cfg.LABELS.index(c[0])]
                    rstring += '{},{},{},{},{:.4f}\n'.format(
                        start,
                        end,
                        label.split('_')[0],
                        label.split('_')[1],
                        c[1])

            # Write result string to file
            if len(rstring) > 0:
                out_string += rstring

    # Save as file
    with open(path, 'w') as rfile:
        rfile.write(out_string)


def getSortedTimestamps(results):
    return sorted(results, key=lambda t: float(t.split('-')[0]))


def getRawAudioFromFile(fpath):

    # Open file
    sig, rate = audio.openAudioFile(fpath, cfg.SAMPLE_RATE)

    # Split into raw audio chunks
    chunks = audio.splitSignal(sig, rate, cfg.SIG_LENGTH, cfg.SIG_OVERLAP, cfg.SIG_MINLEN)

    return chunks

def predict(samples):

    # Prepare sample and pass through model
    data = np.array(samples, dtype='float32')
    prediction = model.predict(data)

    # Logits or sigmoid activations?
    if cfg.APPLY_SIGMOID:
        prediction = model.flat_sigmoid(np.array(prediction), sensitivity=-cfg.SIGMOID_SENSITIVITY)

    return prediction

def analyzeFile(item):

    # Get file path and restore cfg
    fpath = item[0]
    cfg.setConfig(item[1])

    # Start time
    start_time = datetime.datetime.now()

    # Status
    print('Analyzing {}'.format(fpath), flush=True)

    # Open audio file and split into 3-second chunks
    chunks = getRawAudioFromFile(fpath)

    # If no chunks, show error and skip
    if len(chunks) == 0:
        msg = 'Error: Cannot open audio file {}'.format(fpath)
        print(msg, flush=True)
        ## Uncomment if Needed 
        # writeErrorLog(msg) 
        return False

    # Process each chunk
    try:
        start, end = 0, cfg.SIG_LENGTH
        results = {}
        samples = []
        timestamps = []
        for c in range(len(chunks)):

            # Add to batch
            samples.append(chunks[c])
            timestamps.append([start, end])

            # Advance start and end
            start += cfg.SIG_LENGTH - cfg.SIG_OVERLAP
            end = start + cfg.SIG_LENGTH

            # Check if batch is full or last chunk        
            if len(samples) < cfg.BATCH_SIZE and c < len(chunks) - 1:
                continue

            # Predict
            p = predict(samples)

            # Add to results
            for i in range(len(samples)):

                # Get timestamp
                s_start, s_end = timestamps[i]

                # Get prediction
                pred = p[i]

                # Assign scores to labels
                p_labels = dict(zip(cfg.LABELS, pred))

                # Sort by score
                p_sorted =  sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)

                # Store top 5 results and advance indicies
                results[str(s_start) + '-' + str(s_end)] = p_sorted

            # Clear batch
            samples = []
            timestamps = []  
    except:
        # Print traceback
        print(traceback.format_exc(), flush=True)

        # Write error log
        msg = 'Error: Cannot analyze audio file {}.\n{}'.format(fpath, traceback.format_exc())
        print(msg, flush=True)
        ## Uncomment if Needed 
        # writeErrorLog(msg)
        return False     

    # Save as selection table
    try:

        # Make directory if it doesn't exist
        if len(os.path.dirname(cfg.OUTPUT_PATH)) > 0 and not os.path.exists(os.path.dirname(cfg.OUTPUT_PATH)):
            os.makedirs(os.path.dirname(cfg.OUTPUT_PATH), exist_ok=True)

        if os.path.isdir(cfg.OUTPUT_PATH):
            rpath = fpath.replace(cfg.INPUT_PATH, '')
            rpath = rpath[1:] if rpath[0] in ['/', '\\'] else rpath
            if cfg.RESULT_TYPE == 'table':
                rtype = '.BirdNET.selection.table.txt' 
            elif cfg.RESULT_TYPE == 'audacity':
                rtype = '.BirdNET.results.txt'
            else:
                rtype = '.BirdNET.results.csv'
            saveResultFile(results, os.path.join(cfg.OUTPUT_PATH, rpath.rsplit('.', 1)[0] + rtype), fpath)
        else:
            saveResultFile(results, cfg.OUTPUT_PATH, fpath)        
    except:

        # Print traceback
        print(traceback.format_exc(), flush=True)

        # Write error log
        msg = 'Error: Cannot save result for {}.\n{}'.format(fpath, traceback.format_exc())
        print(msg, flush=True)
        ## Uncomment if Needed 
        # writeErrorLog(msg)
        return False

    delta_time = (datetime.datetime.now() - start_time).total_seconds()
    print('Finished {} in {:.2f} seconds'.format(fpath, delta_time), flush=True)

    return True

def getAudioFileName(folderIn):
    dateTimeIn = datetime.datetime.now()
    strOut = str(dateTimeIn)
    strOut = strOut.replace("-","_").replace(" ","_").replace(":","_").replace(".","_")
    return folderIn + "/" + strOut + "/mintsAudio" +".wav"

def getJsonFileName(folderIn,dateTimeIn):
    strOut = str(dateTimeIn)
    strOut = strOut.replace("-","_").replace(" ","_").replace(":","_").replace(".","_")
    return folderIn + "/" + strOut + "_mintsAudio" +".json"


def makeAudioFile2(sampleRateIn,audioLength,channelNum,tmpFolder):
    fileName = getAudioFileName(tmpFolder)
    print("Recording  an audio file to be saved @: " + fileName)
    recording = sd.rec(int(audioLength * sampleRateIn),\
        samplerate=sampleRateIn,\
             channels=channelNum)
    sd.wait()  # Wait until recording is finished
    mSR.directoryCheck(fileName)
    write(fileName,sampleRateIn, recording)  # Save as WAV file
    print("Recording Saved")
    return recording;

def makeAudioFile(sampleRateIn,audioLength,channelNum,fileName,fileSaveLocation):
    
    recording = sd.rec(int(audioLength * sampleRateIn), samplerate=sampleRateIn, channels=channelNum)
    sd.wait()  # Wait until recording is finished
    write(os.path.join(fileSaveLocation,fileName), sampleRateIn, recording)  # Save as WAV file
    return recording;

def configSetUp(cfgIn,outPutPath,confidenceIn,cpuThreads):

    # Parse arguments
    parser = argparse.ArgumentParser(description='Analyze audio files with BirdNET')
    parser.add_argument('--i', default=outPutPath, help='Path to input file or folder. If this is a file, --o needs to be a file too.')
    parser.add_argument('--o', default=outPutPath, help='Path to output file or folder. If this is a file, --i needs to be a file too.')
    parser.add_argument('--lat', type=float, default=32.779167, help='Recording location latitude. Set -1 to ignore.')
    parser.add_argument('--lon', type=float, default=-96.808891, help='Recording location longitude. Set -1 to ignore.')
    parser.add_argument('--week', type=int, default=-1, help='Week of the year when the recording was made. Values in [1, 48] (4 weeks per month). Set -1 for year-round species list.')
    parser.add_argument('--slist', default='', help='Path to species list file or folder. If folder is provided, species list needs to be named \"species_list.txt\". If lat and lon are provided, this list will be ignored.')
    parser.add_argument('--sensitivity', type=float, default=1.0, help='Detection sensitivity; Higher values result in higher sensitivity. Values in [0.5, 1.5]. Defaults to 1.0.')
    parser.add_argument('--min_conf', type=float, default=confidenceIn, help='Minimum confidence threshold. Values in [0.01, 0.99]. Defaults to 0.1.')
    parser.add_argument('--overlap', type=float, default=0.0, help='Overlap of prediction segments. Values in [0.0, 2.9]. Defaults to 0.0.')
    parser.add_argument('--rtype', default='csv', help='Specifies output format. Values in [\'table\', \'audacity\', \'r\', \'csv\']. Defaults to \'table\' (Raven selection table).')
    parser.add_argument('--threads', type=int, default=cpuThreads, help='Number of CPU threads.')
    parser.add_argument('--batchsize', type=int, default=1, help='Number of samples to process at the same time. Defaults to 1.')
    parser.add_argument('--locale', default='en', help='Locale for translated species common names. Values in [\'af\', \'de\', \'it\', ...] Defaults to \'en\'.')
    parser.add_argument('--sf_thresh', type=float, default=0.03, help='Minimum species occurrence frequency threshold for location filter. Values in [0.01, 0.99]. Defaults to 0.03.')

    args = parser.parse_args()

    # Set paths relative to script path (requested in #3)
    cfgIn.MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.MODEL_PATH)
    cfgIn.LABELS_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.LABELS_FILE)
    cfgIn.TRANSLATED_LABELS_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.TRANSLATED_LABELS_PATH)
    cfgIn.MDATA_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.MDATA_MODEL_PATH)
    cfgIn.CODES_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.CODES_FILE)
    cfgIn.ERROR_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), cfgIn.ERROR_LOG_FILE)

    # Load eBird codes, labels
    cfgIn.CODES = loadCodes()
    cfgIn.LABELS = loadLabels(cfgIn.LABELS_FILE)

    # Load translated labels
    lfile = os.path.join(cfgIn.TRANSLATED_LABELS_PATH, os.path.basename(cfgIn.LABELS_FILE).replace('.txt', '_{}.txt'.format(args.locale)))
    if not args.locale in ['en'] and os.path.isfile(lfile):
        cfgIn.TRANSLATED_LABELS = loadLabels(lfile)
    else:
        cfgIn.TRANSLATED_LABELS = cfgIn.LABELS   

    ### Make sure to comment out appropriately if you are not using args. ###

    # Load species list from location filter or provided list
    cfgIn.LATITUDE, cfgIn.LONGITUDE, cfgIn.WEEK = args.lat, args.lon, args.week
    cfgIn.LOCATION_FILTER_THRESHOLD = max(0.01, min(0.99, float(args.sf_thresh)))
    if cfgIn.LATITUDE == -1 and cfgIn.LONGITUDE == -1:
        if len(args.slist) == 0:
            cfgIn.SPECIES_LIST_FILE = None
        else:
            cfgIn.SPECIES_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), args.slist)
            if os.path.isdir(cfgIn.SPECIES_LIST_FILE):
                cfgIn.SPECIES_LIST_FILE = os.path.join(cfgIn.SPECIES_LIST_FILE, 'species_list.txt')
        cfgIn.SPECIES_LIST = loadSpeciesList(cfgIn.SPECIES_LIST_FILE)
    else:
        predictSpeciesList()
    if len(cfgIn.SPECIES_LIST) == 0:
        print('Species list contains {} species'.format(len(cfgIn.LABELS)))
    else:        
        print('Species list contains {} species'.format(len(cfgIn.SPECIES_LIST)))

    # Set input and output path    
    cfgIn.INPUT_PATH = args.i
    cfgIn.OUTPUT_PATH = args.o

    # Parse input files
    if os.path.isdir(cfgIn.INPUT_PATH):
        cfgIn.FILE_LIST = parseInputFiles(cfgIn.INPUT_PATH)  
    else:
        cfgIn.FILE_LIST = [cfgIn.INPUT_PATH]

    # Set confidence threshold
    cfgIn.MIN_CONFIDENCE = max(0.01, min(0.99, float(args.min_conf)))

    # Set sensitivity
    cfgIn.SIGMOID_SENSITIVITY = max(0.5, min(1.0 - (float(args.sensitivity) - 1.0), 1.5))

    # Set overlap
    cfgIn.SIG_OVERLAP = max(0.0, min(2.9, float(args.overlap)))

    # Set result type
    cfgIn.RESULT_TYPE = args.rtype.lower()    
    if not cfgIn.RESULT_TYPE in ['table', 'audacity', 'r', 'csv']:
        cfgIn.RESULT_TYPE = 'table'

    # Set number of threads
    if os.path.isdir(cfgIn.INPUT_PATH):
        cfgIn.CPU_THREADS = max(1, int(args.threads))
        cfgIn.TFLITE_THREADS = 1
    else:
        cfgIn.CPU_THREADS = 1
        cfgIn.TFLITE_THREADS = max(1, int(args.threads))

    # Set batch size
    cfgIn.BATCH_SIZE = max(1, int(args.batchsize))

    # Add config items to each file list entry.
    # We have to do this for Windows which does not
    # support fork() and thus each process has to
    # have its own config. USE LINUX!
    flist = []
    for f in cfgIn.FILE_LIST:
        flist.append((f, cfgIn.getConfig()))

    # Analyze files   
    if cfgIn.CPU_THREADS < 2:
        for entry in flist:
            analyzeFile(entry)
    else:
        with Pool(cfgIn.CPU_THREADS) as p:
            p.map(analyzeFile, flist)


    return cfgIn;

