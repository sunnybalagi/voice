const player = document.getElementById('player');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const uploadButton = document.getElementById('upload');
//const pageIdx = document.getElementById('pageidx')
//const downloadButton = document.getElementById('download');
let shouldStop = false;
let blob;
let mediaRecorder;

navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia;

startButton.onclick = function(e) {
    if (navigator.getUserMedia) {
        navigator.getUserMedia(
            { audio: true, video: false }, handleSuccess, handleError);
    } else {
        console.log("getUserMedia not supported");
    }
};

stopButton.onclick = function(e) {
    mediaRecorder.stop();
}

uploadButton.onclick = async function(e) {
    let form = new FormData();
    if (blob instanceof Blob) {
        form.append('file', blob, 'audio.wav');
        let response = await fetch('/upload/' + pageIdx, {
            method: 'POST',
            body: form,
            credentials: "include",
        });
        window.location.href = '/survey/' + pageIdx;
    } else {
        alert('Please record your voice!');
    }
}

const handleSuccess = function(stream) {
    const options = {mimeType: 'audio/webm'};
    mediaRecorder = new MediaRecorder(stream, options);
    let recordedChunks = [];
    let stopped = false;

    mediaRecorder.onstart = function(e) {
        console.log('start');
    }

    mediaRecorder.ondataavailable = function(e) {
        if (e.data.size > 0) {
            recordedChunks.push(e.data);
        }

        if(shouldStop === true && stopped === false) {
            mediaRecorder.stop();
            console.log('stop');
            stopped = true;
        }
    };

    mediaRecorder.onstop = function(e) {
        blob = new Blob(recordedChunks, { type: 'audio/wav' });
        let url = URL.createObjectURL(blob);
        player.src = url;
    }

    mediaRecorder.start();
    console.log('start recorder ...');
}

const handleError = function(e) {
    console.log(e);
}
