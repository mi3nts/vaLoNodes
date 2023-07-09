#!/bin/bash
sleep 2
kill $(pgrep -f 'python3 a_1_audioRecorder.py')
sleep 2
kill $(pgrep -f 'python3 l_1_loRaSend.py')
sleep 2
kill $(pgrep -f 'a_2_audioAnalyzer.py')


