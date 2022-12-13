from voice_password import app
from flask import request
import os
import numpy as np
import pyaudio
from scipy.io import wavfile
import voice_password.utils as fn

# i=0


@app.route('/saveAndPredict', methods=['POST'])
def saveRecord():
    # global i
    if request.method == 'POST':

        file = request.files['AudioFile']
        file.save(os.path.join(
            'voice_password/static/assets/recorded_audio/recordedAudio.wav'))
        # i+=1

    speakerName = fn.test_model()
    # text = fn.test_speech_model()
    # return [0, 0]
    return [speakerName]
    return [speakerName, text]
