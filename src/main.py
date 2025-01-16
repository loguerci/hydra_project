from audio.audioprocessor import AudioProcessor
from threading import Thread
import time
from webserver.server import WebServer
from event.eventmanager import EventManager

def main():
    event_manager = EventManager()

    web_server = WebServer(event_manager=event_manager)
    audio_processor = AudioProcessor(event_manager=event_manager)

    devices = audio_processor.list_sound_devices()
    for idx, device in enumerate(devices):
        print(f"{idx}: {device['name']}")
    device_index = int(input("Enter the device index: "))
    audio_processor.set_device_index(device_index)

    web_thread = Thread(target=web_server.run, daemon=True)
    audio_thread = Thread(target=audio_processor.start_processing, daemon=True)
    web_thread.start()
    audio_thread.start()

    print("Application started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping application...")
        audio_processor.stop_processing()

if __name__ == '__main__':
    main()