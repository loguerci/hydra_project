# AudioMorph
A visual journey through live sound.

This web-browser based app creates dynamic visuals reactive to music playing from an audio input of your computer. The visuals change based on the genre, mood, energy etc.

## How it works 
It is a Python webserver, which, after being executed serves a webpage where visuals are rendered in real time,
based on audio features extracted from the input you choose.

## Usage
After creating a python environment, 
install the required packages with pip
```bash
pip install -r requirements.txt
```

To launch, you just need to run the main.py file, with (optional) port parameter (default 8080)

```bash
python main.py --port 8080
```

Once the server is running, a list of the available audio devices is printed to the console.
Choose the number corresponding to the microphone/input that you wish to use.

Then, open localhost:8080 in your browser and start experiencing Audiomorph!

## Limitations
- Currently, due to compatibility issues with the Essentia library, the app requires Python version <= 3.12 and NumPy version <= 1.26.4.
- The app does not run on Windows systems at the moment.

## Contributions
Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request with your improvements.
