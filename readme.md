# AudioMorph
A visual journey through live sound

It Creates dynamic visuals reactive to music, reacting to an audio input of your computer

## How it works 
It's a pythong webserver, that after being executed serves a webpage where visuals are rendered in real time,
based on audio features extracted from the input you choose

## Usage
after creating a python environment, 
install the required packages with pip
```bash
pip install -r requirements.txt
```

To launch, you just need to run the main.py file, with (optional) port parameter (default 8080)

```bash
python main.py --port 8080
```

Once the server is running, a list of the available audio devices is printed to the console,
choose the number corresponding to the microphone/input that you want to use

Then, open localhost:8080 in your browser and start experiencing Audiomorph!

## Limitations
- Currently, due to compatibility issues with the Essentia library, the app requires Python version <= 3.12 and NumPy version <= 1.26.4.
- The app does not run on Windows systems at the moment.

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request with your improvements.
