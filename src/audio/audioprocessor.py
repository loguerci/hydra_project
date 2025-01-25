import pyaudio
import sounddevice as sd
import numpy as np
import json
import librosa
import time
from threading import Thread
from multiprocessing import Process
from audio.HLFProcessor import HLFProcessor
from multiprocessing import Queue
from queue import Empty

#this class process the audio signal that comes from the input
#there are two types of processing, the first one that calculates
#features using the librosa library and the second one that calculates
#high level features using the class HLFProcessor

class AudioProcessor:
    def __init__(self, event_manager):
        self.pa = pyaudio.PyAudio()
        self.format = pyaudio.paFloat32
        self.channels=1
        #the buffer size parameter can be modified, it will affect the frequency of the calculation of features with librosa
        self.buffer_size=512
        self.event_manager = event_manager
        #this queue is necessary to pass data from the HLFProcessor to this class, because the HLFProcessor runs in a separate thread to avoid lags
        self.hlf_queue = Queue()
        self.hlf_processor = HLFProcessor(buffer_size=self.buffer_size, output_queue=self.hlf_queue)
        self.hlf_thread = Process(target=self.hlf_processor.process)
        


    #this method uses librosa to calculate some features, you can add here all the other features you need
    def calculate_fft_and_rms(self, signal):
        D = librosa.stft(signal, n_fft=self.buffer_size)
        magnitude, phase = librosa.magphase(D)
        mag_db = librosa.amplitude_to_db(magnitude)
        rms = float(librosa.feature.rms(y=signal, frame_length=self.buffer_size, hop_length=self.buffer_size).mean())
        freqs = librosa.core.fft_frequencies(sr=self.sample_rate)
        low_freq = 200
        mid_freq = 1000
        high_freq = 5000
        low_idx = np.where(freqs <= low_freq)[0][-1]
        mid_idx = np.where((freqs > low_freq) & (freqs <= mid_freq))[0][-1]
        high_idx = np.where((freqs > mid_freq) & (freqs <= high_freq))[0][-1]  
        low_band_energy = float(np.mean(mag_db[:low_idx]))
        mid_band_energy = float(np.mean(mag_db[low_idx:mid_idx]))
        high_band_energy = float(np.mean(mag_db[mid_idx:high_idx]))     
        self.event_manager.publish("audio_data", json.dumps({'bass': low_band_energy, 'mid': mid_band_energy, 'high': high_band_energy, 'rms': rms}))


    #this method is called every time an audio frame is acquired from the input

    def process_audio_frames(self, in_data, frame_count, time_info, status):
        start_time = time.time()
        signal = np.frombuffer(in_data, dtype=np.float32)
        self.hlf_processor.add_frame(signal.copy())
        self.calculate_fft_and_rms(signal.copy())
        end_time = time.time()
        elapsed_time = end_time - start_time
        return(in_data, pyaudio.paContinue)

    def list_sound_devices(self):
        return sd.query_devices()
    
    def set_device_index(self, index):
        self.device_index = index


    def start_processing(self):
        self.running = True
        input_device = self.pa.get_device_info_by_index(self.device_index)
        self.sample_rate = int(input_device['defaultSampleRate'])
        self.hlf_processor.set_sample_rate(self.sample_rate)
        self.hlf_thread.start()
        self.hlf_queue_thread = Thread(target=self.process_hlf_queue)
        self.hlf_queue_thread.start()
        self.stream = self.pa.open(format=self.format,
                                   input=True,
                                   channels=self.channels,
                                   rate=self.sample_rate,
                                   frames_per_buffer=self.buffer_size,
                                   input_device_index=self.device_index,
                                   stream_callback=self.process_audio_frames)

    def process_hlf_queue(self):
        while self.running:
            try:
                message = self.hlf_queue.get(timeout=0.1)
                self.event_manager.publish("hlf-data", json.dumps(message))
            except Empty:
                continue





    def stop_processing(self):
        self.running = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
        self.hlf_processor.stop()
        self.hlf_thread.join()
        self.hlf_queue_thread.join()
        print("Audio processing stopped.")