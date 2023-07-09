# Updates for a new OdroidC4 Ubuntu Image

- Pip Insall 
```
sudo apt update
sudo apt install python3-pip
```
- Adding User (teamlary) to the the audio group 
```
sudo addgroup teamlary audio
```
- Installing Audio Libraries 
```
pip3 install sounddevice
sudo apt-get install libportaudio2
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
pip3 install librosa==0.9.1
```

- USB Power Control Depenndancies
```
sudo apt install libusb-1.0-0-dev
git clone https://github.com/mvp/uhubctl
cd uhubctl/
make
sudo make install
```
- Installing firmware dependancies 
```
pip3 install paho-mqtt
pip3 install pyserial
pip3 install getmac
pip3 install pynmea2
pip3 install scipy
pip3  install pandas
pip3 install numpy==1.21
```

- Installing I2C dependancies
```
pip3 install smbus2
```

- Installing Tensor Flow for Audio Analysis 
```
pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

- To take care of the following error 
```
scikit_learn.libs/libgomp-d22c30c5.so.1.0.0: cannot allocate memory in static TLS block
```
Adding the following to the ~.bashrc 
```
export LD_PRELOAD=/home/teamlary/.local/lib/python3.8/site-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0
```
