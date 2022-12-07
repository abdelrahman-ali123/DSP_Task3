from sklearn.mixture import GaussianMixture
from scipy.io.wavfile import read
from scipy.signal import get_window
from python_speech_features import mfcc
from sklearn import preprocessing
import scipy.fftpack as fft
import numpy as np
import warnings
import pyaudio
import pickle
import time
import wave
import os
import librosa


warnings.filterwarnings("ignore")


def calculate_delta(array):

    rows, cols = array.shape
    deltas = np.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first = 0
            else:
                first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]]-array[index[0][1]] +
                     (2 * (array[index[1][0]]-array[index[1][1]]))) / 10
    return deltas


def extract_features(audio, sample_rate):
    mfcc_feature = mfcc(audio, sample_rate, 0.025,
                        0.01, 20, nfft=1200, appendEnergy=True)
    mfcc_feature = preprocessing.scale(mfcc_feature)
    # print(mfcc_feature)
    delta = calculate_delta(mfcc_feature)
    combined = np.hstack((mfcc_feature, delta))
    return combined


def test_model():

    audio_path = "voice_password\\static\\assets\\recorded_audio\\recordedAudio.wav"
    modelpath = "voice_password\\static\\assets\\voice_models\\"

    gmm_files = [os.path.join(modelpath, fname) for fname in
                os.listdir(modelpath) if fname.endswith('.gmm')]

    # Load the Gaussian Models
    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    speakers = [fname.split("\\")[-1].split(".gmm")[0] for fname
                in gmm_files]

    audio, sr = librosa.load(audio_path)

    vector = extract_features(audio, sr)
    log_likelihood = np.zeros(len(models))

    for i in range(len(models)):
        print(models)
        gmm = models[i]  # checking with each model one by one
        scores = np.array(gmm.score(vector))
        print(scores)
        log_likelihood[i] = scores.sum()

    winner = np.argmax(log_likelihood)
    # print("\tdetected as - ", speakers[winner])
    time.sleep(1.0)

    return speakers[winner]



def test_speech_model():

    audio_path = "voice_password\\static\\assets\\recorded_audio\\recordedAudio.wav"
    modelpath = "voice_password\\static\\assets\\text_models\\"

    gmm_files = [os.path.join(modelpath, fname) for fname in
                os.listdir(modelpath) if fname.endswith('.gmm')]

    # Load the Gaussian gender Models
    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    speakers = [fname.split("\\")[-1].split(".gmm")[0] for fname
                in gmm_files]

    audio, sr = librosa.load(audio_path)
    vector = extract_features(audio, sr)
    log_likelihood = np.zeros(len(models))

    for i in range(len(models)):
        gmm = models[i]  # checking with each model one by one
        scores = np.array(gmm.score(vector))
        # print(scores)
        log_likelihood[i] = scores.sum()

    winner = np.argmax(log_likelihood)
    # print("\tdetected as - ", speakers[winner])
    time.sleep(1.0)
    return speakers[winner]