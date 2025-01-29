from src.audio.audioprocessor import AudioProcessor
from threading import Thread
import time
from src.webserver.server import WebServer
from src.event.eventmanager import EventManager
import logging
import argparse


logging.basicConfig(
    level=logging.INFO,  # Livello predefinito
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main(port):
    #the event manager purpose is to exchange data from the audio processor to the web server
    event_manager = EventManager()

    web_server = WebServer(event_manager=event_manager, port=port)
    audio_processor = AudioProcessor(event_manager=event_manager)

    #ask for the audio input
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
        web_thread.join()
        audio_thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if (args.debug):
        logging.getLogger().setLevel(logging.DEBUG)
    main(args.port)