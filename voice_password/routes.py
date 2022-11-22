from voice_password import app 
from flask import request
import os
import librosa
import numpy as np
from scipy.io import wavfile




@app.route('/saveRecord', methods = ['POST'])
def saveRecord():
    if request.method == 'POST':
        file = request.files['AudioFile']
        file.save(os.path.join('voice_password/static/assets/recorded_audio/recordedAudio.wav'))
        sr, audio = wavfile.read('voice_password/static/assets/recorded_audio/recordedAudio.wav')
        
        if len(audio.shape)>1:
            audio=audio[:,0]
    return[]