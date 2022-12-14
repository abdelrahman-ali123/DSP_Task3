URL = window.URL || window.webkitURL;

var gumStream; //stream from getUserMedia()
var rec; //Recorder.js object
var input; //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //audio context to help us record

var recordButton = document.getElementById("recordButton");
var title = document.getElementById("title");

//add events to those 2 buttons
recordButton.addEventListener("click",  (e)=>{
  let elem = e.target;
  elem.classList.toggle('active');
  startRecording()
  // elem.classList.toggle('active');
  setTimeout(()=>{
    elem.classList.toggle('active')
  }, 3000)


});

function startRecording() {
    /*
            Simple constraints object, for more advanced audio features see
            https://addpipe.com/blog/audio-constraints-getusermedia/
        */

    var constraints = { audio: true, video: false };

    /*
            Disable the record button until we get a success or fail from getUserMedia() 
        */

    recordButton.disabled = true;

  /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

    navigator.mediaDevices
        .getUserMedia(constraints)
        .then(function (stream) {


/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
    audioContext = new AudioContext();

      //update the format
    

      /*  assign to gumStream for later use  */
    gumStream = stream;

      /* use the stream */
    input = audioContext.createMediaStreamSource(stream);

      /* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
    rec = new Recorder(input, { numChannels: 1 });
   
      //start the recording process
    rec.record();
          setTimeout(stopRecording, 3000)

    })
    .catch(function (err) {
      //enable the record button if getUserMedia() fails
    recordButton.disabled = false;
    });
}



function stopRecording() {

//disable the stop button, enable the record too allow for new recordings
recordButton.disabled = false;


//tell the recorder to stop the recording
rec.stop();

//stop microphone access
gumStream.getAudioTracks()[0].stop();

//create the wav blob and pass it on to createDownloadLink
rec.exportWAV(saveRecord);
}

let input_data = {
    x: [],
    y: [],
    name:'input' ,
    mode: 'markers',
    type: 'scatter',
    marker:{size:12}
}
let Abdelrahman_data = {
  x: [],
  y: [],
  name:'Abelrahamn' ,
  mode: 'markers',
  type: 'scatter'}

let Maye_data = {
  x: [],
  y: [],
  name:'Maye' ,
  mode: 'markers',
  type: 'scatter'
}
let Mohamed_data = {
  x: [],
  y: [],
  name:'Mohamed' ,
  mode: 'markers',
  type: 'scatter'}

let Yousef_data = {
  x: [],
  y: [],
  name:'Yousef' ,
  mode: 'markers',
  type: 'scatter'} 

  let layout = {
    xaxis:{title:'Feature1'},
    yaxis:{title:'Feature2'}
  }
// Plotly.newPlot('plot', [data]);
let speaker;
let result = document.getElementById('result')
let saveRecord = (audioBlob) => {
    let formdata = new FormData();
    formdata.append("AudioFile", audioBlob, "recordedAudio.wav");
    $.ajax({
        type: "POST",
        url: `http://127.0.0.1:5000/saveAndPredict`,
        data: formdata,
        contentType: false,
        cache: false,
        processData: false,
        success: function (res) {
        speaker = res[0];
        input_data.x = [res[1][0]]
        input_data.y = [res[1][1]]
        Abdelrahman_data.x = res[2].slice(0,10)
        Abdelrahman_data.y = res[3].slice(0,10)
        Maye_data.x = res[2].slice(10,20)
        Maye_data.y = res[3].slice(10,20)
        Mohamed_data.x = res[2].slice(20,30)
        Mohamed_data.y = res[3].slice(20,30)
        Yousef_data.x = res[2].slice(30,40)
        Yousef_data.y = res[3].slice(30,40)
        result.innerText= speaker 
        console.log(input_data)
        Plotly.newPlot('plot', [Abdelrahman_data, Maye_data, Mohamed_data, Yousef_data, input_data], layout);
        title.innerText = 'Most recognized features in your voice'

        }
    });
};


