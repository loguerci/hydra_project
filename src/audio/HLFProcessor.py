from multiprocessing import Queue
from queue import Empty
import numpy as np
from essentia.streaming import VectorInput, FrameCutter, TensorflowInputMusiCNN, VectorRealToTensor, TensorToPool, TensorflowPredict, PoolToTensor, TensorToVectorReal
from essentia import Pool, reset, run
import os
import librosa
import json
import time
from .Smoother import Smoother

class HLFProcessor:
    def __init__(self, buffer_size, output_queue, target_rate=16000, sample_rate=48000):
        self.sample_rate = sample_rate
        self.target_rate = target_rate
        self.buffer_size = buffer_size
        self.frame_queue = Queue()
        self.running = False
        self.accumulated_signal = np.array([], dtype=np.float32)
        self.output_queue = output_queue
        self.smoother = Smoother()
    
    
    def process(self):
        self.setup_model()
        self.running = True
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1)
                self.accumulated_signal = np.append(self.accumulated_signal, frame)
                if len(self.accumulated_signal) >= self.buffer_duration * self.target_rate:
                    signal_to_process = self.accumulated_signal[:self.buffer_size]
                    self.accumulated_signal = self.accumulated_signal[self.buffer_size:]
                    self.run_model(signal_to_process)
                
            except Empty:
                continue


    def run_model(self, signal):
        current_time = time.time()
        # print("model running at time: ", current_time)
        self.buffer[:] = signal.flatten()
        reset(self.vimp)
        run(self.vimp)
        data = {
            'danceability': self.pool['danceability'][0][0],
            'aggressive': self.pool['aggressive'][0][0],
            'happy': self.pool['happy'][0][0],
            'party': self.pool['party'][0][0],
            'acoustic': self.pool['acoustic'][0][0],
            'atonal': self.pool['atonal'][0][0],
            'relaxed': 1 - self.pool['relaxed'][0][0],
            'genre': self.pool['genre'][0],
            'genre_labels': self.genre_classes
        }
        smoothed_data = self.smoother.smooth(data)
        self.output_queue.put(smoothed_data)
        danceability = smoothed_data['danceability']
        aggressive =  smoothed_data['aggressive']
        happy = smoothed_data['happy']
        party = smoothed_data['party']
        acoustic = smoothed_data['acoustic']
        atonal = smoothed_data['atonal']
        relaxed = 1 - smoothed_data['relaxed']
        genre = smoothed_data['genre']

        print(f"danceability:  {danceability:.2f}")
        print(f"aggressive:  {aggressive:.2f}")
        print(f"happy:  {happy:.2f}")
        print(f"party:  {party:.2f}")
        print(f"acoustic:  {acoustic:.2f}")
        print(f"atonal:  {atonal:.2f}")
        print(f"relaxed:  {relaxed:.2f}")
        genre_index = np.argmax(genre)
        genre_label = self.genre_classes[genre_index]
        genre_value = genre[genre_index]
        print(f"genre: {genre_label} ({genre_value:.2f})")

        # print(self.pool['danceability'])
        print(" ")
        self.pool.clear()


        
    def add_frame(self, frame):
        resampled_frame = librosa.resample(frame, orig_sr=self.sample_rate, target_sr=self.target_rate)
        self.frame_queue.put(resampled_frame)

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def stop(self):
        self.running = False


    def setup_model(self):
        print("Setting up model...", flush=True)
        self.input_layer = 'model/Placeholder'
        self.output_layer = 'model/Sigmoid'
        self.hop_size = 256
        self.patch_size = 96
        self.number_bands = 96
        self.buffer_size = self.hop_size * self.patch_size
        self.buffer_duration = self.buffer_size / self.target_rate

        self.buffer = np.zeros(self.buffer_size, dtype='float32')

        self.vimp = VectorInput(self.buffer)
        self.fc = FrameCutter(frameSize=512, hopSize=self.hop_size)
        self.tim = TensorflowInputMusiCNN()
        self.vtt = VectorRealToTensor(shape=[1, 1, self.patch_size, self.number_bands], lastPatchMode='discard')
        self.ttp = TensorToPool(namespace=self.input_layer)

        current_dir = os.path.dirname(__file__)
        danceability_path = os.path.abspath(os.path.join(current_dir, '../../models', 'danceability-musicnn-msd-1.pb'))
        aggressiveness_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_aggressive-musicnn-msd-1.pb'))
        happy_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_happy-musicnn-msd-1.pb'))
        party_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_party-musicnn-msd-1.pb'))
        acoustics_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_acoustic-musicnn-msd-1.pb'))
        atonal_path = os.path.abspath(os.path.join(current_dir, '../../models', 'tonal_atonal-musicnn-msd-1.pb'))
        relaxed_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_relaxed-musicnn-msd-1.pb'))
        genre_path = os.path.abspath(os.path.join(current_dir, '../../models', 'msd-musicnn-1.pb'))
        genre_metadata_path = os.path.abspath(os.path.join(current_dir, '../../models', 'msd-musicnn-1.json'))
        with open(genre_metadata_path, 'r') as json_file:
            self.genre_metadata = json.load(json_file)
        self.genre_classes = self.genre_metadata['classes']
        self.n_classes = len(self.genre_classes)

        self.tfp_danceability = TensorflowPredict(graphFilename=danceability_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_aggressive = TensorflowPredict(graphFilename=aggressiveness_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_happy = TensorflowPredict(graphFilename=happy_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_party = TensorflowPredict(graphFilename=party_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_acoustic = TensorflowPredict(graphFilename=acoustics_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_atonal = TensorflowPredict(graphFilename=atonal_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_relaxed = TensorflowPredict(graphFilename=relaxed_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        self.tfp_genre = TensorflowPredict(graphFilename=genre_path,
                        inputs=[self.input_layer],
                        outputs=[self.output_layer])
        
        self.ptt_danceability = PoolToTensor(namespace=self.output_layer)
        self.ptt_aggressive = PoolToTensor(namespace=self.output_layer)
        self.ptt_happy = PoolToTensor(namespace=self.output_layer)
        self.ptt_party = PoolToTensor(namespace=self.output_layer)
        self.ptt_acoustic = PoolToTensor(namespace=self.output_layer)
        self.ptt_atonal = PoolToTensor(namespace=self.output_layer)
        self.ptt_relaxed = PoolToTensor(namespace=self.output_layer)
        self.ptt_genre = PoolToTensor(namespace=self.output_layer)

        self.ttv_danceability = TensorToVectorReal()
        self.ttv_aggressive = TensorToVectorReal()
        self.ttv_happy = TensorToVectorReal()
        self.ttv_party = TensorToVectorReal()
        self.ttv_acoustic = TensorToVectorReal()
        self.ttv_atonal = TensorToVectorReal()
        self.ttv_relaxed = TensorToVectorReal()
        self.ttv_genre = TensorToVectorReal()

        self.pool = Pool()

        self.vimp.data >> self.fc.signal
        self.fc.frame >> self.tim.frame
        self.tim.bands >> self.vtt.frame
        self.vtt.tensor >> self.ttp.tensor

        self.ttp.pool >> self.tfp_danceability.poolIn
        self.ttp.pool >> self.tfp_aggressive.poolIn
        self.ttp.pool >> self.tfp_happy.poolIn
        self.ttp.pool >> self.tfp_party.poolIn
        self.ttp.pool >> self.tfp_acoustic.poolIn
        self.ttp.pool >> self.tfp_atonal.poolIn
        self.ttp.pool >> self.tfp_relaxed.poolIn
        self.ttp.pool >> self.tfp_genre.poolIn

        self.tfp_danceability.poolOut >> self.ptt_danceability.pool
        self.tfp_aggressive.poolOut >> self.ptt_aggressive.pool
        self.tfp_happy.poolOut >> self.ptt_happy.pool
        self.tfp_party.poolOut >> self.ptt_party.pool
        self.tfp_acoustic.poolOut >> self.ptt_acoustic.pool
        self.tfp_atonal.poolOut >> self.ptt_atonal.pool
        self.tfp_relaxed.poolOut >> self.ptt_relaxed.pool
        self.tfp_genre.poolOut >> self.ptt_genre.pool

        self.ptt_danceability.tensor >> self.ttv_danceability.tensor
        self.ptt_aggressive.tensor >> self.ttv_aggressive.tensor
        self.ptt_happy.tensor >> self.ttv_happy.tensor
        self.ptt_party.tensor >> self.ttv_party.tensor
        self.ptt_acoustic.tensor >> self.ttv_acoustic.tensor
        self.ptt_atonal.tensor >> self.ttv_atonal.tensor
        self.ptt_relaxed.tensor >> self.ttv_relaxed.tensor
        self.ptt_genre.tensor >> self.ttv_genre.tensor

        self.ttv_danceability.frame >> (self.pool, 'danceability')
        self.ttv_aggressive.frame >> (self.pool, 'aggressive')
        self.ttv_happy.frame >> (self.pool, 'happy')
        self.ttv_party.frame >> (self.pool, 'party')
        self.ttv_acoustic.frame >> (self.pool, 'acoustic')
        self.ttv_atonal.frame >> (self.pool, 'atonal')
        self.ttv_relaxed.frame >> (self.pool, 'relaxed')
        self.ttv_genre.frame >> (self.pool, 'genre')