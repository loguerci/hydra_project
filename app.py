#*************************************************************************************
#                                   CPAC Project
#                         Aesthetic representation of music
#                                   Loïs Guerci
#                                      2024
#*************************************************************************************

# Here is the python module to initialize the webpage app & process the audio file 
# given by the user

# command line usage : "python app.py path/to/audio.file"

import sys
import librosa
import json
import numpy as np
from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit
import time
import sounddevice as sd
import scipy.signal
import pyaudio
import aubio
from time import sleep

bufferSize = 512
windowSizeMultiple = 2

#index of microphone input
audioInputDeviceIndex = 3
audioInputChannels = 1

hopSize = bufferSize
winSize = hopSize * windowSizeMultiple
pa = pyaudio.PyAudio()
print(pa.get_device_info_by_index(audioInputDeviceIndex))
audioInputDevice = pa.get_device_info_by_index(audioInputDeviceIndex)
audioInputSampleRate = int(audioInputDevice['defaultSampleRate'])
tempoDetection = aubio.tempo(method='default', buf_size=winSize, hop_size=hopSize, samplerate=audioInputSampleRate)



# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

def readAudioFrames(in_data, frame_count, time_info, status):
 
    signal = np.frombuffer(in_data, dtype=np.float32)
    beat = tempoDetection(signal)
    if beat:
        bpm = tempoDetection.get_bpm()
        confidence = tempoDetection.get_confidence()
        tempoDetection.set_threshold(0.5)
        tempoDetection.set_silence(-30)
        socketio.emit('beat_detected', json.dumps({"pulse": True}))
        print("beat! (running with "+str(bpm)+" bpm) confidence: " + str(confidence))
    return (in_data, pyaudio.paContinue)



if len(sys.argv) < 2:
    print("Usage: python app.py <audio_file>")
    #sys.exit(1)
    AUDIO_FILE_PATH = 'static/test.mp3'
else:
    AUDIO_FILE_PATH = sys.argv[1] 

@app.route('/')
def init():
    audio_url = url_for('static', filename=AUDIO_FILE_PATH.split('/')[-1])
    return render_template('render.html', audio_url=audio_url)

@socketio.on('start_analysis')
def start_analysis():
    print("start analysis")
    audio_path = AUDIO_FILE_PATH
    y, sr = librosa.load(audio_path)
    
    rms = float(librosa.feature.rms(y=y).mean())
    cent = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    mfcc = float(librosa.feature.mfcc(y=y, sr=sr).mean())
    flat = float(librosa.feature.spectral_flatness(y=y).mean())
    bpm = int(librosa.feature.tempo(y=y, sr=sr)+1)
    print(bpm)

    emit('audio_feature', json.dumps({"cent": cent,
                                      "rms": rms,
                                      "mfcc": mfcc,
                                      "bpm": bpm,
                                      "flat": flat}))
    pulse = 0

    
    
    inputStream = pa.open(format=pyaudio.paFloat32,
                input=True,
                channels=audioInputChannels,
                input_device_index=audioInputDeviceIndex,
                frames_per_buffer=bufferSize,
                rate=audioInputSampleRate,
                stream_callback=readAudioFrames)

if __name__ == '__main__':
    socketio.run(app, port=8080) 
