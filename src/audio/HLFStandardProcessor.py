from multiprocessing import Queue
from queue import Empty
import numpy as np
import os
import json
import time
from .Smoother import Smoother
import librosa

class HLFStandardProcessor:
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

        
    def run_model(self, signal):
        audio = signal.flatten()
        # genre_labels, genre_predictions = self.process_genres(self.genre_classes, genre_predictions[0])
        genre_labels = ['Blues', 'Brass & Military', "Children's", "Classical", "Electronic", "Folk, World & Country",
                        "Funk / Soul", "Hip Hop", "Jazz", "Latin", "Non-Music", "Pop", "Reggae", "Rock", "Stage & Screen"]
        genre_predictions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        smoothed_data = {
            'danceability': 0.1,
            'aggressive': 0.3,
            'happy': 0.5,
            'party': 0.2,
            'acoustic': 0.2,
            'atonal': 0.2,
            'relaxed': 0.2,
            'genre': genre_predictions,
            'genre_labels': genre_labels
        }
        # smoothed_data = self.smoother.smooth(data)
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
        print(f"genre: {genre_label} ({genre_value:.2f})")


    def process_genres(self, classes, values):
        main_labels = np.array([clazz.split('---')[0] for clazz in classes])
        unique_labels = np.unique(main_labels)
        summed_values = np.array([values[main_labels == label].sum() for label in unique_labels])
        return unique_labels, summed_values
