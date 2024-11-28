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
from beat_this.inference import File2Beats

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

if len(sys.argv) < 2:
    print("Usage: python app.py <audio_file>")
    sys.exit(1)

AUDIO_FILE_PATH = sys.argv[1] 

@app.route('/')
def init():
    audio_url = url_for('static', filename=AUDIO_FILE_PATH.split('/')[-1])
    return render_template('render.html', audio_url=audio_url)

@socketio.on('start_analysis')
def start_analysis():
    audio_path = AUDIO_FILE_PATH
    y, sr = librosa.load(audio_path)
    
    rms = float(librosa.feature.rms(y=y).mean())
    cent = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    mfcc = float(librosa.feature.mfcc(y=y, sr=sr).mean())
    flat = float(librosa.feature.spectral_flatness(y=y).mean())
    file2beats = File2Beats(checkpoint_path="final0", dbn=False)
    beats,downbeats = file2beats(audio_path)
    bpm = int(librosa.feature.tempo(y=y, sr=sr)+1)
    print(bpm)

    emit('audio_feature', json.dumps({"cent": cent,
                                      "rms": rms,
                                      "mfcc": mfcc,
                                      "bpm": bpm,
                                      "flat": flat}))
    pulse = 0
    # Emulate a real-time feed by emitting data at intervals
    for i, beat_time in enumerate(beats):
        next_beat_time = beats[i + 1] if i < len(beats) - 1 else beats[i]
        if i%2 == 0: pulse = 2
        else: pulse = 2.5

        emit('beat_detected', json.dumps({"pulse": pulse}))
        time.sleep(next_beat_time - beat_time)  # Sleep until the next beat

if __name__ == '__main__':
    socketio.run(app) 
