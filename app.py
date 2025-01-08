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
from essentia.standard import *
#from scrap_music import download_yt



def genre_recognition(audio_path):
    with open('discogs-effnet-bs64-1.json', 'r') as json_file:
        metadata = json.load(json_file)
    audio = MonoLoader(filename=audio_path, sampleRate=16000, resampleQuality=4)()
    embedding_model = essentia.standard.TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)
    model = TensorflowPredict2D(graphFilename="genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    predictions = model(embeddings)
    index = np.argmax(np.sum(predictions, axis=0))
    return metadata['classes'][index]

def find_genre_index(tag, genres):
    return next((i for i, genre in enumerate(genres) if tag.startswith(genre)), -1)


# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

if len(sys.argv) < 2:
    print("Usage: python app.py <audio_file>")
    sys.exit(1)

#download_yt(sys.argv[1])
#AUDIO_FILE_PATH = 'static/test.mp3'
AUDIO_FILE_PATH = sys.argv[1] #delete this line

@app.route('/')
def init():
    audio_url = url_for('static', filename=AUDIO_FILE_PATH.split('/')[-1])
    return render_template('render.html', audio_url=audio_url)

@socketio.on('start_analysis')
def start_analysis():
    audio_path = AUDIO_FILE_PATH
    y, sr = librosa.load(audio_path)

    genre = genre_recognition(audio_path)
    print(genre)
    
    genres = ['Electronic', 'Latin', 'Rock']
    genre_index  = find_genre_index(genre, genres)
    print(genre_index)
    
    # Extraction Audio Features
    rms = float(librosa.feature.rms(y=y).mean())
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo[0])
    chroma = (librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1)).tolist()
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    mels = librosa.power_to_db(S, ref=np.max)
    low_band = float(mels[0:40, :].mean())
    mid_band = float(mels[40:80, :].mean())
    high_band = float(mels[80:, :].mean())

    # Extraction Real time BPM (with exact time code for each beats)
    file2beats = File2Beats(checkpoint_path="final0", dbn=False)
    beats,downbeats = file2beats(audio_path)

    emit('audio_feature', json.dumps({
        "genre": genre_index,
        "rms": rms,
        "bpm": bpm,
        "chroma": chroma,
        "low_band": low_band,
        "mid_band": mid_band,
        "high_band": high_band}))
    
    pulse = 0
    # Emulate a real-time feed by emitting data at intervals
    for i, beat_time in enumerate(beats):
        next_beat_time = beats[i + 1] if i < len(beats) - 1 else beats[i]
        if i%2 == 0: pulse = 2
        else: pulse = 2.5

        emit('beat_detected', json.dumps({"pulse": pulse}))
        time.sleep(next_beat_time - beat_time)  # Sleep until the next beat

if __name__ == '__main__':
    socketio.run(app, port=8080) 
