import os
import sys
import requests
import json 
import csv
import ffmpeg
import numpy as np
from pathlib import Path
from yt_dlp import YoutubeDL

# things to do :
# - pip install yt_dlp
# - pip install ffmpeg


def download_yt(music_url):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '\static\test.%(ext)s')

    ydl_opts = {
    'format': 'mp3/bestaudio/best',
    'outtmpl': output_dir,
    'quality':0,
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        }]
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(music_url, download=False)
        video_title = info_dict.get('title', None)
        if video_title:
            print(f'Video title: {video_title}')
        ydl.download([music_url])

if __name__ == '__main__':
    input_file = sys.argv[1]
    download_yt(input_file)