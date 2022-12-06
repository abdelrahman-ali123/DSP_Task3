from voice_password import app
from flask import request
import os
import numpy as np
from scipy.io import wavfile
import voice_password.utils as fn


@app.route('/saveAndPredict', methods=['POST'])
def saveRecord():
    if request.method == 'POST':
        file = request.files['AudioFile']
        file.save(os.path.join(
            'voice_password/static/assets/recorded_audio/recordedAudio.wav'))

    speakerName = fn.test_model()
    return [speakerName]
