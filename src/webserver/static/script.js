/************************************************************************************
                                    CPAC Project
                          Aesthetic representation of music
                                    Loïs Guerci
                                       2024
*************************************************************************************/

/* Here is the javascript module which will create the visual with Hydra Video Synth 
   based on the python module results */

   const hydraScript = document.createElement('script');

    let dampedGenres = [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0];
    let targetGenres = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
    const alpha = 0.2;
    const alpha_features  = 0.4;
   
   const socket = io();
   const hydra = new Hydra();
   let scale = 1;

   let dampedAudioFeatures = {
        aggressive: 0,
        danceability: 0,
        party: 0,
        acoustic: 0,
        atonal: 0,
        relaxed: 0
   }

   let targetAudioFeatures = {
        aggressive: 0,
        danceability: 0,
        party: 0,
        acoustic: 0,
        atonal: 0,
        relaxed: 0
   }

   
   
   let audioFeatures = {
       bass: 0,
       mid: 0,
       high: 0,
       rms: 0,
       happy: 0,
       aggressive: 0,
   };

    

    socket.on('audio_data', (data) => {
        const parsedData = JSON.parse(data);
        scale = parsedData.bass;
        audioFeatures.bass = parsedData.bass;
        audioFeatures.mid = parsedData.mid;
        audioFeatures.high = parsedData.high;
        audioFeatures.rms = parsedData.rms;
        audioFeatures.mfcc = parsedData.mfcc;
    });
   
   socket.on('hlf-data', (data) => {
       const parsedData = JSON.parse(data);
   
       targetAudioFeatures.happy = parsedData.happy;
       targetAudioFeatures.aggressive = parsedData.aggressive;
       targetAudioFeatures.danceability = parsedData.danceability;
       targetAudioFeatures.party = parsedData.party;
       targetAudioFeatures.acoustic = parsedData.acoustic;
       targetAudioFeatures.atonal = parsedData.atonal;
       targetAudioFeatures.relaxed = parsedData.relaxed;
       targetGenres = parsedData.genre;
    
   });


    const blues = osc(audioFeatures.bass / 20, audioFeatures.rms * 0.3, 0.5)
                    .color(0.2, 0.4, 0.7)
                    .modulate(noise(audioFeatures.rms * 2), 0.1);

    const brassAndMilitary = shape(6, 0.4, 0.8)
                    .color(1, 0.8, 0.3)
                    .rotate(() => audioFeatures.bass * 0.05)
                    .modulatePixelate(osc(20, 0.2, 0.5), 15);
    
    const childrens = voronoi(10 + audioFeatures.bass, 0.3, 0.5)
                    .color(1, 0.8, 1)
                    .modulate(osc(5, 0.1, 0.3), 0.2);

    const classical = shape(4, 0.1 + dampedAudioFeatures.relaxed * 2)
                    .color(0.8, 0.7, 0.6)
                    .modulate(noise(audioFeatures.rms * 10), 0.1);

    const electronic = osc(20, 0.01, 1.1)
	.kaleid(5)
	.color(()=> dampedAudioFeatures.aggressive*2, ()=> dampedAudioFeatures.happy*2, ()=> dampedAudioFeatures.relaxed)
	.rotate(0, 0.1)
	.modulate(o0, () => audioFeatures.bass * 0.02)
	.scale(1.01);

    const folkworldandcountry = voronoi(10,0.6,10) //Adjust the second parameter for evolution speed.
    .add(osc(1,0,10)).kaleid(21)
    .scale(1,1,2).colorama();
    // src(o1).mult(src(s0).modulateRotate(o1,100), -0.5)
    //   .out(o0)
    

    const funkSoul = 
    osc([1, 2, 3, 4], 0.4, 5).color(()=> dampedAudioFeatures.aggressive*2, ()=> dampedAudioFeatures.happy*2, ()=> dampedAudioFeatures.relaxed).rotate(0.3, 0.1).add(noise(1.5, 1), 10).modulate(noise(1.5, 1), 10);

    const hipHop = shape(100,0.5,1.5)
    .scale(()=> dampedAudioFeatures.aggressive,()=> audioFeatures.bass * 0.2)
    .color([1, 0, 1]  //modulate the second parameter of color to change from colour to colour
    .smooth(1),0.3,0)
    .repeat(2,2)
    .modulateScale(osc(3,0.5),-0.6)
    .add(o0,0.5).modulateRotate(noise(3).thresh(0,0), Math.PI/2)
    .scale(0.9);

    const jazz = gradient(0.3 + audioFeatures.rms, 0.3)
                    .color(0.5, 0.7, 0.3)
                    .modulate(noise(dampedAudioFeatures.danceability), 0.2);

    const latin = osc(25, 0.3, 0.5)
                    .color(1, 0.6, 0.2)
                    .rotate(() => dampedAudioFeatures.party * 0.1)
                    .modulateRotate(voronoi(10, 0.3), 0.1);

    const nonMusic = osc(50).color(1,0,0).scale(()=>audioFeatures.bass);

    const pop = voronoi(10 + audioFeatures.bass, 0.3, audioFeatures.rms * 5)
                       .modulateRotate(osc(10, 0.1, 0.5), dampedAudioFeatures.danceability * 0.2);

    const reggae = shape(3, 0.3, 0.7)
                       .color(0.3, 1, 0.5)
                       .rotate(() => dampedAudioFeatures.relaxed * 0.1)
                       .modulate(noise(audioFeatures.bass * 0.2), 0.2);

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

    const stageandscreen = gradient(audioFeatures.rms, 0.2)
                        .color(0.7, 0.3, 0.6)
                        .modulate(osc(5, 0.1), 0.1);

    const deflt =  osc(50).color(1,1,0).scale(()=>audioFeatures.bass).out();



    

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

    const genresDict = {
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

    function updateOutput() {
        const topGenreIndex = dampedGenres.indexOf(Math.max(...dampedGenres));
        const maxVal = Math.max(...dampedGenres);
        const filteredArray = dampedGenres.filter(val => val !== maxVal);
        const secondMaxVal = Math.max(...filteredArray);
        const secondMaxIndex = dampedGenres.indexOf(secondMaxVal);
        let mainVisual = genresDict[genreMap[topGenreIndex]];
        let secondVisual = genresDict[genreMap[secondMaxIndex]];
        let proportion = secondMaxVal/maxVal;
        proportion = proportion/2;
        // console.log(topGenreIndex);
        // console.log(secondMaxIndex);
        // console.log(proportion);
        proportion = makeExponentialProportion(proportion);
        // console.log(proportion);
        mainVisual.out(o1);
        secondVisual.out(o2);
        src(o1).blend(o2, proportion).out();
        // render(o3);
    }

    function makeExponentialProportion(p) {
        return Math.pow(10, 4*p)/200;
    }

    setInterval(updateOutput, 50);

    function dampGenres() {
        //a.map((val, index) => alpha * val - (1 - alpha) * (b[index] || 0));
        // console.log(dampedGenres);
        // console.log(targetGenres);
        dampedGenres = dampedGenres.map((val, index) => alpha * targetGenres[index] + (1-alpha) * val);
        // console.log(dampedGenres);
    }

    setInterval(dampGenres, 200);

    function dampAudioFeatures() {
        console.log("damping")
        Object.keys(dampedAudioFeatures).forEach(key => {
            dampedAudioFeatures[key] = targetAudioFeatures[key] * alpha_features  + dampedAudioFeatures[key] * (1-alpha_features);
        });
        console.log(targetAudioFeatures);
        console.log(dampedAudioFeatures);
   }

   setInterval(dampAudioFeatures, 200);

   
   console.log("Press 'Enter' to start audio analysis.");
   
   document.head.appendChild(hydraScript);
   
   socket.emit('connected');
   


   