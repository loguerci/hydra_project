/************************************************************************************
                                    CPAC Project
                          Aesthetic representation of music
                                    Loïs Guerci
                                       2024
*************************************************************************************/

/* Here is the javascript module which will create the visual with Hydra Video Synth 
   based on the python module results */

const hydraScript = document.createElement('script');
hydraScript.src = '/static/hydra-synth.js';
hydraScript.onload = () => {

    const socket = io();
    const hydra = new Hydra();
    var x = document.getElementById("background-audio")

    // Set up visuals
    let firstVisualShown = false;

    //collect audio features from python module
    socket.on('audio_feature', (data) => {
        const parsedData = JSON.parse(data)
        rms = parsedData.rms
        cent = parsedData.cent
        mfcc = parsedData.mfcc
        bpm = parsedData.bpm
        flat = parsedData.flat
    });

    // Update visuals based on audio data
    socket.on('beat_detected', (beat) => {
        const parsedData = JSON.parse(beat)
        pulse = parsedData.pulse

        a.setBins(5)

        //Visual
        osc(pulse*10,(bpm/1000),0.5).kaleid(cent*50)
        .color(rms*20,mfcc*2.5,flat*100).blend(noise(() => a.fft[0]*4))
        .out()
        a.setSmooth(.8) // audio reactivity smoothness from 0 to 1, uses linear interpolation
        a.setScale(8)    // loudness upper limit (maps to 0)
        a.setCutoff(0.1)   // loudness from which to start listening to (maps to 0)
        a.show() // show what hydra's listening to


        render(o0)

        // the music starts when the first visual is shown
        if (!firstVisualShown) {
            x.play().then(() => {
                console.log("Audio synchronized with first visual");
            }).catch((error) => {
                console.error("Audio play failed:", error);
            });
            firstVisualShown = true; // Ensure this only happens once
    }    
    });

 
    
    document.addEventListener('keydown', (event) => {
        if (event.key === "Enter") {
            socket.emit('start_analysis'); // Start analysis on user interaction
            console.log("Analysis started, waiting for first visual to play audio.");
        }
    });

    // Optional: Provide feedback for the user to press "Enter"
    console.log("Press 'Enter' to start audio analysis.");
};

document.head.appendChild(hydraScript);