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
   
   let audioFeatures = {
       bass: 0,
       mid: 0,
       high: 0,
       rms: 0,
       mfcc: [],
       happy: 0,
       aggressive: 0,
       danceability: 0,
       party: 0,
       acoustic: 0,
       atonal: 0,
       relaxed: 0,
       genre: [],
       bpm: 0,
   };
    socket.on('audio_data', (data) => {
        const parsedData = JSON.parse(data);
        scale = parsedData.bass;
        audioFeatures.bass = parsedData.bass;
        audioFeatures.mid = parsedData.mid;
        audioFeatures.high = parsedData.high;
        audioFeatures.rms = parsedData.rms;
        audioFeatures.mfcc = parsedData.mfcc;
        audioFeatures.bpm = parsedData.bpm;
        console.log('Updated audioFeatures (low-level):', audioFeatures);
    });
   
   socket.on('hlf-data', (data) => {
       const parsedData = JSON.parse(data);
   
       audioFeatures.happy = parsedData.happy;
       audioFeatures.aggressive = parsedData.aggressive;
       audioFeatures.danceability = parsedData.danceability;
       audioFeatures.party = parsedData.party;
       audioFeatures.acoustic = parsedData.acoustic;
       audioFeatures.atonal = parsedData.atonal;
       audioFeatures.relaxed = parsedData.relaxed;
       console.log('Updated audioFeatures (high-level):', audioFeatures);
       audioFeatures.genre = parsedData.genre;

       const highestGenreIndex = audioFeatures.genre.indexOf(Math.max(...audioFeatures.genre));

       const genreArray = audioFeatures.genre;

        const maxVal = Math.max(...genreArray);

        const filteredArray = genreArray.filter(val => val !== maxVal);

        const secondMaxVal = Math.max(...filteredArray);

        const secondMaxIndex = genreArray.indexOf(secondMaxVal);

        console.log(secondMaxIndex);



       const genreMap = [
           "Blues",
           "Brass & Military",
           "Children's",
           "Classical",
           "Electronic",
           "Folk, World & Country",
           "Funk / Soul",
           "Hip Hop",
           "Jazz",
           "Latin",
           "Non-Music",
           "Pop",
           "Reggae",
           "Rock",
           "Stage & Screen",
       ];
       const currentGenre = genreMap[highestGenreIndex]; // Map the index to a genre name
       const secondGenre = genreMap[secondMaxIndex];

       const proportion = secondMaxVal/maxVal;

       const dict = {
        "Blues" : blues,
        "Brass & Military": brassAndMilitary,
           "Children's" : childrens,
           "Classical" : classical,
           "Electronic" : electronic,
           "Folk, World & Country" : folkworldandcountry,
           "Funk / Soul" : funkSoul,
           "Hip Hop" : hipHop,
           "Jazz" : jazz,
           "Latin" : latin,
           "Non-Music" : nonMusic,
           "Pop" : pop,
           "Reggae" : reggae,
           "Rock" : rock,
           "Stage & Screen" : stageandscreen,
       }

       let visual = dict[currentGenre];
       let visual2 = dict[secondGenre];
       console.log(visual);
       console.log(visual2);
       console.log(proportion);
       //visual.out(o1);
       //visual2.out(o2);
       //render();
      // visual.blend(visual2).out();
       visual.out();
   });

   let bass = 0;
   let rms = 0;
   let relaxed = 0;
   let time = 0;
   let danceability = 0;
   let happy = 0;
   let party = 0;
   let atonal = 0;

    const blues = osc(bass / 20, rms * 0.3, 0.5)
                    .color(0.2, 0.4, 0.7)
                    .modulate(noise(rms * 2), 0.1);

    const brassAndMilitary = shape(6, 0.4, 0.8)
                    .color(1, 0.8, 0.3)
                    .rotate(() => bass * 0.05)
                    .modulatePixelate(osc(20, 0.2, 0.5), 15);
    
    const childrens = voronoi(10 + bass, 0.3, 0.5)
                    .color(1, 0.8, 1)
                    .modulate(osc(5, 0.1, 0.3), 0.2);

    const classical = shape(4, 0.1 + relaxed * 2)
                    .color(0.8, 0.7, 0.6)
                    .modulate(noise(rms * 10), 0.1);

    const electronic = osc(20, 0.01, 1.1)
	.kaleid(5)
	.color(()=> audioFeatures.aggressive*2, ()=> audioFeatures.happy*2, ()=> audioFeatures.relaxed)
	.rotate(0, 0.1)
	.modulate(o0, () => audioFeatures.bass * 0.02)
	.scale(1.01);

    const folkworldandcountry = voronoi(10,0.6,10) //Adjust the second parameter for evolution speed.
    .add(osc(1,0,10)).kaleid(21)
    .scale(1,1,2).colorama().out(o1)
    src(o1).mult(src(s0).modulateRotate(o1,100), -0.5)
      .out(o0)
    

    const funkSoul = 
    osc([1, 2, 3, 4], 0.4, 5).color(()=> audioFeatures.aggressive*2, ()=> audioFeatures.happy*2, ()=> audioFeatures.relaxed).rotate(0.3, 0.1).add(noise(1.5, 1), 10).modulate(noise(1.5, 1), 10);

    const hipHop = shape(100,0.5,1.5)
    .scale(()=> audioFeatures.aggressive,()=> audioFeatures.bass * 0.2)
    .color([1, 0, 1]  //modulate the second parameter of color to change from colour to colour
    .smooth(1),0.3,0)
    .repeat(2,2)
    .modulateScale(osc(3,0.5),-0.6)
    .add(o0,0.5).modulateRotate(noise(3).thresh(0,0), Math.PI/2)
    .scale(0.9);

    const jazz = gradient(0.3 + rms, 0.3)
                    .color(0.5, 0.7, 0.3)
                    .modulate(noise(danceability), 0.2);

    const latin = osc(25, 0.3, 0.5)
                    .color(1, 0.6, 0.2)
                    .rotate(() => party * 0.1)
                    .modulateRotate(voronoi(10, 0.3), 0.1);

    const nonMusic = osc(50).color(1,0,0).scale(()=>audioFeatures.bass);

    const pop = voronoi(10 + bass, 0.3, rms * 5)
                       .modulateRotate(osc(10, 0.1, 0.5), danceability * 0.2);

    const reggae = shape(3, 0.3, 0.7)
                       .color(0.3, 1, 0.5)
                       .rotate(() => relaxed * 0.1)
                       .modulate(noise(bass * 0.2), 0.2);

    const rock = noise(18)
    .colorama(1)
    .posterize(2)
    .kaleid(50)
    .mask(
      shape(25, 0.25).modulateScale(
        noise(400.5, 0.5)
      )
    )
    .mask(shape(400, 1, 2.125))
    .modulateScale(osc(6, 0.125, 0.05).kaleid(50))
    .mult(osc(100, 0.05, 2.4).kaleid(50), 0.25)
    .scale(1.75, 0.65, 0.5)
    .modulate(noise(()=> audioFeatures.bass/2))
    .saturate(6)
    .posterize(4, 0.2)
    .scale(1.5);

    const stageandscreen = gradient(rms, 0.2)
                        .color(0.7, 0.3, 0.6)
                        .modulate(osc(5, 0.1), 0.1);

    const deflt =  osc(50).color(1,1,0).scale(()=>audioFeatures.bass).out();


    
    


    function setupVisual() {
        deflt.out();
    }


//    setInterval(() => {
//        const {
//            bass,
//            rms,
//            mfcc,
//            danceability,
//            relaxed,
//            happy,
//            party,
//            atonal,
//            aggressive,
//            genre,
//        } = audioFeatures;
   
//        // Find the genre with the highest probability
//        const highestGenreIndex = genre.indexOf(Math.max(...genre));
//        const genreMap = [
//            "Blues",
//            "Brass & Military",
//            "Children's",
//            "Classical",
//            "Electronic",
//            "Folk, World & Country",
//            "Funk / Soul",
//            "Hip Hop",
//            "Jazz",
//            "Latin",
//            "Non-Music",
//            "Pop",
//            "Reggae",
//            "Rock",
//            "Stage & Screen",
//        ];
//        const currentGenre = genreMap[highestGenreIndex]; // Map the index to a genre name
   
//        console.log("Current genre:", currentGenre);
   
//        // Define genre-based template visuals
//        let visual;
   
//        switch (currentGenre) {
//            case "Blues":
//                visual = osc(bass / 20, rms * 0.3, 0.5)
//                    .color(0.2, 0.4, 0.7)
//                    .modulate(noise(rms * 2), 0.1);
//                break;
//            case "Brass & Military":
//                visual = shape(6, 0.4, 0.8)
//                    .color(1, 0.8, 0.3)
//                    .rotate(() => bass * 0.05)
//                    .modulatePixelate(osc(20, 0.2, 0.5), 15);
//                break;
//            case "Children's":
//                visual = voronoi(10 + bass, 0.3, 0.5)
//                    .color(1, 0.8, 1)
//                    .modulate(osc(5, 0.1, 0.3), 0.2);
//                break;
//            case "Classical":
//                visual = shape(4, 0.1 + relaxed * 2)
//                    .color(0.8, 0.7, 0.6)
//                    .modulate(noise(rms * 10), 0.1);
//                break;
//                case "Electronic":
//                    visual = osc(10, 0.1, 0.8) // Oscillator pattern for base visuals
//                        .rotate(() => time * 0.1, 0.1) // Slow rotation for the tunnel
//                        .modulateScale(noise(3, () => rms * 2), 0.5) // Add depth and scale variation based on RMS
//                        .modulateRotate(osc(5, 0.2, 0.5), danceability * 0.2) // Twisting effect based on danceability
//                        .kaleid(4) // Symmetry for the tunnel structure
//                        .color(0.8, 0.5 + relaxed * 0.5,  rms * 100 + happy*10) // Dynamic color changes
//                        .scale(() => 1 + bass / 10); // Tunnel expands and contracts with bass
//                    break;            
//            case "Folk, World & Country":
//                visual = osc(bass / 15, 0.2, 0.7)
//                    .color(0.6, 0.4, 0.2)
//                    .modulate(noise(2), 0.2);
//                break;
//            case "Funk / Soul":
//                visual = shape(5, 0.3, 0.7)
//                    .color(1, 0.5, 0.2)
//                    .modulateRotate(osc(15, 0.3, 0.5), danceability * 0.2);
//                break;
//            case "Hip Hop":
//                visual = voronoi(15, 0.2, rms * 2)
//                    .color(0.7, 0.4, 0.3)
//                    .modulatePixelate(noise(bass * 2), 20);
//                break;
//            case "Jazz":
//                visual = gradient(0.3 + rms, 0.3)
//                    .color(0.5, 0.7, 0.3)
//                    .modulate(noise(danceability), 0.2);
//                break;
//            case "Latin":
//                visual = osc(25, 0.3, 0.5)
//                    .color(1, 0.6, 0.2)
//                    .rotate(() => party * 0.1)
//                    .modulateRotate(voronoi(10, 0.3), 0.1);
//                break;
//                case "Non-Music":
//                    visual = noise(() => atonal*100/bass, () => rms * 5) // Base noise pattern
//                        .modulate(noise(() => rms * 500, 0.3), () => rms*1000) // Disruptive modulation
//                        .color(0.9, 0.9, 0.9) // Monochromatic effect
//                        .contrast(1.5) // Enhance sharpness
//                        .brightness(-0.5) // Slight dimming
//                        .scale(() => 1 + rms * 1000); // Dynamic scaling with RMS
//                    break;            
//            case "Pop":
//                visual = voronoi(10 + bass, 0.3, rms * 5)
//                    .modulateRotate(osc(10, 0.1, 0.5), danceability * 0.2);
//                break;
//            case "Reggae":
//                visual = shape(3, 0.3, 0.7)
//                    .color(0.3, 1, 0.5)
//                    .rotate(() => relaxed * 0.1)
//                    .modulate(noise(bass * 0.2), 0.2);
//                break;
//            case "Rock":
//                visual = noise(bass * 5, rms * 0.3)
//                    .color(1, 0.5, 0.3)
//                    .modulatePixelate(osc(5, rms * 0.2), bass * 2);
//                break;
//            case "Stage & Screen":
//                visual = gradient(rms, 0.2)
//                    .color(0.7, 0.3, 0.6)
//                    .modulate(osc(5, 0.1), 0.1);
//                break;
//            default:
//                visual = osc(bass / 10, rms * 0.5, 0.8); // Default visuals
//                break;
//        }
   
//        // Adjust visuals based on mood
//        visual = visual
//        .color(
//            1 - happy * 5,             // Happy: Add subtle red tint (scaled up)
//            0.5 + relaxed * 2,         // Relaxed: Amplify green channel effect
//            0.8 + aggressive * 3       // Aggressive: Stronger blue tint for intensity
//        )
//        .rotate(() => party * 1)       // Amplify rotational movement (scaled up)
//        .scale(() => 1 + rms * 2)      // Scale more noticeably with loudness
//        .modulate(noise(mfcc[9] / 2), 0.2); // Stronger texture modulation
   
   
//        // Output the visuals
//        visual.out();
//    }, 150);
   
   
   console.log("Press 'Enter' to start audio analysis.");
   
   document.head.appendChild(hydraScript);
   
   socket.emit('connected');

  // setupVisual();
   
   //pulse decay function
   let targetValue = 2;
   let decayRate = 1;
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


   