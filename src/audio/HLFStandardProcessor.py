from multiprocessing import Queue
from queue import Empty
import numpy as np
import os
import json
from .Smoother import Smoother
import librosa
from essentia.standard import TensorflowPredictEffnetDiscogs, TensorflowPredict2D
from src.utils import normalize_array

class HLFStandardProcessor:
    def __init__(self, buffer_size, output_queue, target_rate=16000, sample_rate=48000):
        self.sample_rate = sample_rate
        self.target_rate = target_rate
        self.buffer_size = buffer_size
        self.frame_queue = Queue()
        self.running = False
        self.accumulated_signal = np.array([], dtype=np.float32)
        self.output_queue = output_queue
        self.smoother = Smoother(alpha=0.5)

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

    def add_frame(self, frame):
        resampled_frame = librosa.resample(frame, orig_sr=self.sample_rate, target_sr=self.target_rate)
        self.frame_queue.put(resampled_frame)

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def stop(self):
        self.running = False

    def setup_model(self):
        self.buffer_size = 48348
        self.buffer_duration = (self.buffer_size / self.target_rate)
        current_dir = os.path.dirname(__file__)
        embeddings_path = os.path.abspath(os.path.join(current_dir, '../../models', 'discogs-effnet-bs64-1.pb'))
        genre_metadata_path = os.path.abspath(os.path.join(current_dir, '../../models', 'genre_discogs400-discogs-effnet-1.json'))
        genre_path = os.path.abspath(os.path.join(current_dir, '../../models', 'genre_discogs400-discogs-effnet-1.pb'))
        danceability_path = os.path.abspath(os.path.join(current_dir, '../../models', 'danceability-discogs-effnet-1.pb'))
        acoustic_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_acoustic-discogs-effnet-1.pb'))
        aggressive_path = os.path.abspath(os.path.join(current_dir, '../../models', 'mood_aggressive-discogs-effnet-1.pb'))
        happy_path = os.path.abspath(os.path.join(current_dir, '../../models', "mood_happy-discogs-effnet-1.pb"))
        party_path = os.path.abspath(os.path.join(current_dir, '../../models', "mood_party-discogs-effnet-1.pb"))
        relax_path = os.path.abspath(os.path.join(current_dir, '../../models', "mood_relaxed-discogs-effnet-1.pb"))
        atonal_path = os.path.abspath(os.path.join(current_dir, '../../models', "tonal_atonal-discogs-effnet-1.pb"))
        with open(genre_metadata_path, 'r') as json_file:
            self.genre_metadata = json.load(json_file)
        self.genre_classes = self.genre_metadata['classes']
        self.embeddings_model = TensorflowPredictEffnetDiscogs(graphFilename=embeddings_path, output='PartitionedCall:1')
        self.genre_model = TensorflowPredict2D(graphFilename=genre_path, input="serving_default_model_Placeholder", output="PartitionedCall:0")
        self.danceability_model = TensorflowPredict2D(graphFilename=danceability_path, output="model/Softmax")
        self.acoustic_model = TensorflowPredict2D(graphFilename=acoustic_path, output="model/Softmax")
        self.aggressive_model = TensorflowPredict2D(graphFilename=aggressive_path, output="model/Softmax")
        self.happy_model = TensorflowPredict2D(graphFilename=happy_path, output="model/Softmax")
        self.party_model = TensorflowPredict2D(graphFilename=party_path, output="model/Softmax")
        self.relax_model = TensorflowPredict2D(graphFilename=relax_path, output="model/Softmax")
        self.atonal_model = TensorflowPredict2D(graphFilename=atonal_path, output="model/Softmax")
        
    def run_model(self, signal):
        audio = signal.flatten()
        embeddings = self.embeddings_model(audio)
        genre_predictions = self.genre_model(embeddings)
        genre_labels, genre_predictions = self.process_genres(self.genre_classes, genre_predictions)
        danceability = self.danceability_model(embeddings)
        acousticness = self.acoustic_model(embeddings)
        aggressive = self.aggressive_model(embeddings)
        happy = self.happy_model(embeddings)
        party = self.party_model(embeddings)
        relax = self.relax_model(embeddings)
        atonal = self.atonal_model(embeddings)
        data = {
            'danceability': danceability[0][0],
            'aggressive': aggressive[0][0],
            'happy': happy[0][0],
            'party': 1 - party[0][0],
            'acoustic': acousticness[0][0],
            'atonal': atonal[0][0],
            'relaxed': relax[0][0],
            'genre': genre_predictions,
            'genre_labels': genre_labels
        }
        smoothed_data = self.smoother.smooth(data)
        smoothed_data['genre'] = normalize_array(smoothed_data['genre'])
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
        genre_label = genre_labels[genre_index]
        genre_value = genre[genre_index]

        genre_copy = genre.copy();
        genre_copy[genre_index] = -np.inf
        genre_index_2 = np.argmax(genre_copy)
        genre_label_2 = genre_labels[genre_index_2]
        genre_value_2 = genre[genre_index_2]
        print(f"genre: {genre_label} ({genre_value:.2f})")
        print(f"genre 2: {genre_label_2} ({genre_value_2:.2f})")


    def process_genres(self, labels, values):
        values = np.sum(values, axis=0)
        main_labels = np.array([label.split('---')[0] for label in labels])
        unique_labels = np.unique(main_labels)
        summed_values = np.array([values[main_labels == label].max() for label in unique_labels])
        return unique_labels, summed_values
