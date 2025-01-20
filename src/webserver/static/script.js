/************************************************************************************
                                    CPAC Project
                          Aesthetic representation of music
                                    Loïs Guerci
                                       2024
*************************************************************************************/

/* Here is the javascript module which will create the visual with Hydra Video Synth 
   based on the python module results */

const hydraScript = document.createElement('script');
// hydraScript.src = '/static/hydra-synth.js';
// hydraScript.onload = () => {

const socket = io();
const hydra = new Hydra();
let scale = 1;
osc(50).color(1,0,0).scale(() => scale).out();
socket.on('audio_data', (data) => {
    const parsedData = JSON.parse(data);
    console.log(parsedData);
    scale = parsedData.bass;
    // triggerDecay();
    // scale = 3;
    // setTimeout(1000)
    // scale = 1;
})
    // var x = document.getElementById("background-audio")

    // Set up visuals
    // let firstVisualShown = false;

    //collect audio features from python module
    // socket.on('audio_feature', (data) => {
    //     const parsedData = JSON.parse(data)
    //     rms = parsedData.rms
    //     cent = parsedData.cent
    //     mfcc = parsedData.mfcc
    //     bpm = parsedData.bpm
    //     flat = parsedData.flat
    // });

    // Update visuals based on audio data
    // socket.on('beat_detected', (beat) => {
    //     const parsedData = JSON.parse(beat)
    //     pulse = parsedData.pulse

    //     a.setBins(5)

    //     //Visual
    //     osc(pulse*10,(bpm/1000),0.5).kaleid(cent*50)
    //     .color(rms*20,mfcc*2.5,flat*100).blend(noise(() => a.fft[0]*4))
    //     .out()
    //     a.setSmooth(.8) // audio reactivity smoothness from 0 to 1, uses linear interpolation
    //     a.setScale(8)    // loudness upper limit (maps to 0)
    //     a.setCutoff(0.1)   // loudness from which to start listening to (maps to 0)
    //     a.show() // show what hydra's listening to


    //     render(o0)

    //     // the music starts when the first visual is shown
    // //     if (!firstVisualShown) {
    // //         x.play().then(() => {
    // //             console.log("Audio synchronized with first visual");
    // //         }).catch((error) => {
    // //             console.error("Audio play failed:", error);
    // //         });
    // //         firstVisualShown = true; // Ensure this only happens once
    // // }    
    // });

 
    
    // document.addEventListener('keydown', (event) => {
    //     if (event.key === "Enter") {
    //         socket.emit('connect'); // Start analysis on user interaction
    //         console.log("Analysis started, waiting for first visual to play audio.");
    //     }
    // });

    // Optional: Provide feedback for the user to press "Enter"
console.log("Press 'Enter' to start audio analysis.");
// };

document.head.appendChild(hydraScript);

socket.emit('connected');

//pulse decay function
let targetValue = 2;
let decayRate = 10;
let isEventTriggered = false;
let startTime = null;

function decay(call) {
    console.log(call);
    if (isEventTriggered) {
        if (startTime === null) {
            startTime = Date.now();
            scale = targetValue;
        }

        let elapsedTime = (Date.now() - startTime) / 1000;

        scale = targetValue * Math.exp(-decayRate * elapsedTime);

        if (scale < 1.05) {
            scale = 1;
            isEventTriggered = false;
        }

        console.log(scale);
        setTimeout(() => decay(call+1), 50);
    }
}

function triggerDecay() {
    isEventTriggered = true;
    startTime = null;
    decay(1);
}
