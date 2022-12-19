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
    data_to_draw = fn.plot_input_features()
    data_to_draw = [float(a) for a in data_to_draw]
    x_data, y_data = fn.plot_trained_featutes()
    return [speakerName, data_to_draw, x_data.tolist(), y_data.tolist()]
