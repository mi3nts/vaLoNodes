#!/bin/bash
sleep 20
export LD_PRELOAD=/home/teamlary/.local/lib/python3.8/site-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0
sleep 20
sleep 10
kill $(pgrep -f 'python3 d_1_deleter.py')
sleep 5
python3 d_1_deleter.py &
sleep 5
sleep 10
kill $(pgrep -f 'python3 a_1_audioRecorder.py')
sleep 5
python3 a_1_audioRecorder.py &
sleep 5

kill $(pgrep -f 'python3 l_1_loRaSend.py')
sleep 5
python3 l_1_loRaSend.py &
sleep 5

kill $(pgrep -f 'a_2_audioAnalyzer.py')
sleep 5
python3 a_2_audioAnalyzer.py &
sleep 5