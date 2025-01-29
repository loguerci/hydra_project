from flask import Flask, render_template 
from flask_socketio import SocketIO
import logging


logger = logging.getLogger(__name__)

#this class is the webserver, its purpose are to send the html page
#and to send the websocket messages with the data acquired from the audio input

class WebServer:
    def __init__(self, event_manager, host='0.0.0.0', port=8080):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.host = host
        self.port = port
        self.event_manager = event_manager

        @self.app.route('/') 
        def index():
            return render_template('render.html')
        
        @self.socketio.on('connected')
        def user_connected():
            logger.info("user connected")

        self.event_manager.subscribe("audio_data", self.send_audio_data)
        self.event_manager.subscribe("hlf-data", self.send_hlf_data)

    def send_audio_data(self, data):
        self.socketio.emit('audio_data', data)

    def send_hlf_data(self, data):
        self.socketio.emit("hlf-data", data)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)