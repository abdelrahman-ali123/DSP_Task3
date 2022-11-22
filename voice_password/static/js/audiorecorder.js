let preview = document.getElementById("preview");
let recording = document.getElementById("recording");
let startButton = document.getElementById("startButton");
let stopButton = document.getElementById("stopButton");
let downloadButton = document.getElementById("downloadButton");
let logElement = document.getElementById("log");
let audioContext = new AudioContext

let recordingTimeMS = 5000;

function log(msg) {
    logElement.innerHTML += `${msg}\n`;
}

function wait(delayInMS) {
    return new Promise((resolve) => setTimeout(resolve, delayInMS));
}


async function startRecording(stream, lengthInMS) {
    const workerOptions = {
        OggOpusEncoderWasmPath: 'https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/OggOpusEncoder.wasm',
        WebMOpusEncoderWasmPath: 'https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/WebMOpusEncoder.wasm'
      };
    // let recorder = new MediaRecorder(stream, {}, workerOptions);
    input = audioContext.createMediaStreamSource(stream)
    let recorder = new WebAudioRecorder(input, { workerDir: "static/js/"});
    let data = [];

    recorder.ondataavailable = (event) => data.push(event.data);
    recorder.startRecording();
    log(`${recorder.state} for ${lengthInMS / 1000} seconds…`);

    let stopped = new Promise((resolve, reject) => {
        recorder.onstop = resolve;
        recorder.onerror = (event) => reject(event.name);
    });

    let recorded = wait(lengthInMS).then(
        () => {
        if (recorder.state === "recording") {
            recorder.stop();
        }
        },
    );

    return Promise.all([
        stopped,
        recorded
    ])
    .then(() => data);
    }


function stop(stream) {
stream.getTracks().forEach((track) => track.stop());
}



startButton.addEventListener("click", () => {
    navigator.mediaDevices.getUserMedia({
        audio: true
    }).then((stream) => {
        preview.srcObject = stream;
        downloadButton.href = stream;
        preview.captureStream = preview.captureStream || preview.mozCaptureStream;
        return new Promise((resolve) => preview.onplaying = resolve);
    }).then(() => startRecording(preview.captureStream(), recordingTimeMS))
    .then ((recordedChunks) => {
        recordedChunks = encodeWav(recordedChunks)
        let recordedBlob = new Blob(recordedChunks, { type: 'audio/wav' });
        recording.src = URL.createObjectURL(recordedBlob);
        downloadButton.href = recording.src;
        downloadButton.download = "RecordedVideo.wav";
        saveRecord(recordedBlob)
    
        log(`Successfully recorded ${recordedBlob.size} bytes of ${recordedBlob.type} media.`);
    })
    .catch((error) => {
        if (error.name === "NotFoundError") {
        log("Camera or microphone not found. Can't record.");
        } else {
        log(error);
        }
    });
    }, false);



stopButton.addEventListener("click", () => {
    stop(preview.srcObject);
    }, false);



let saveRecord = (audioBlob)=>{
    let formdata = new FormData();  
    formdata.append("AudioFile", audioBlob , "recordedAudio.wav");
    $.ajax({
        type: 'POST',
        url: `http://127.0.0.1:5000/saveRecord`,
        data: formdata,
        contentType: false,
        cache: false,
        processData: false,
        success: function(res) {
            console.log(res[1])
        },
    });
}
