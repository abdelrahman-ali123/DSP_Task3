from sklearn.mixture import GaussianMixture
from scipy.io.wavfile import read
from scipy.signal import get_window
import scipy.fftpack as fft
import numpy as np
import warnings
import pyaudio
import pickle
import time
import wave
import os


warnings.filterwarnings("ignore")


def extract_features(audio, rate):
    hop_size = 15  # ms
    FFT_size = 2048

    audio = normalize_audio(audio)
    audio_framed = frame_audio(audio, FFT_size, hop_size, rate)

    # The FFT assumes the audio to be periodic and continues
    # By framing the signal we assured the audio to be periodic
    # To make the audio continues, we apply a window function on every frame
    window = get_window("hann", FFT_size, fftbins=True)
    audio_win = audio_framed * window

    # Then we perform the FFT. After we do the FFT we only take the the positive part of the spectrum (first half +1).
    audio_winT = np.transpose(audio_win)

    audio_fft = np.empty(
        (int(1 + FFT_size // 2), audio_winT.shape[1]), dtype=np.complex64, order='F')

    for n in range(audio_fft.shape[1]):
        audio_fft[:, n] = fft.fft(audio_winT[:, n], axis=0)[
            :audio_fft.shape[0]]

    audio_fft = np.transpose(audio_fft)

    # Calculate signal power
    audio_power = np.square(np.abs(audio_fft))

    # Here we compute the MEL-spaced filterbank and then pass the framed audio through them. That will give us information about the power in each frequency band.
    freq_min = 0
    freq_high = rate / 2
    mel_filter_num = 10
    filter_points, mel_freqs = get_filter_points(
        freq_min, freq_high, mel_filter_num, FFT_size, rate)
    filters = get_filters(filter_points, FFT_size)

    # Next we divide the triangular MEL weights by the width of the MEL band (area normalization).
    # If we wont normalize the filters, we will see the noise increase with frequency because of the filter width.
    enorm = 2.0 / (mel_freqs[2:mel_filter_num+2] - mel_freqs[:mel_filter_num])
    filters *= enorm[:, np.newaxis]

    # Signal Filteration
    audio_filtered = np.dot(filters, np.transpose(audio_power))
    audio_log = 10.0 * np.log10(audio_filtered)

    # Last step is using Discrete Cosine Transform (DCT) to generate cepstral coefficents
    dct_filter_num = 40
    dct_filters = dct(dct_filter_num, mel_filter_num)
    cepstral_coefficents = np.dot(dct_filters, audio_log)

    return cepstral_coefficents


# We first normalize our audio by adding low pass filter (All LPF has a pass-band, stop-band and transition band)
def normalize_audio(audio):
    audio = audio / np.max(np.abs(audio))
    return audio

# Here comes the part of audio framing, where we divide the audio into chunks(frames) will be the same size as the FFT


def frame_audio(audio, FFT_size, hop_size, sample_rate):
    # hop_size in ms

    audio = np.pad(audio, int(FFT_size / 2), mode='reflect')
    audio = audio[:, 0]  # Stereo to only mono
    frame_len = np.round(sample_rate * hop_size / 1000).astype(int)
    frame_num = int((len(audio) - FFT_size) / frame_len) + 1
    frames = np.zeros((frame_num, FFT_size))

    for n in range(frame_num):
        frames[n] = audio[n*frame_len:n*frame_len+FFT_size]

    return frames


# First we construct filter points that determines the start and stop of the filters. To do that we first convert the two filterbank edges to the MEL space
# After that we construct a lineary spaced array between the two MEL frequencies
# Then we convert the array to the frequency space and finally we normalize the array to the FFT size and choose the associated FFT values.
def freq_to_mel(freq):
    return 2595.0 * np.log10(1.0 + freq / 700.0)


def met_to_freq(mels):
    return 700.0 * (10.0**(mels / 2595.0) - 1.0)


def get_filter_points(fmin, fmax, mel_filter_num, FFT_size, sample_rate=44100):
    fmin_mel = freq_to_mel(fmin)
    fmax_mel = freq_to_mel(fmax)

    mels = np.linspace(fmin_mel, fmax_mel, num=mel_filter_num+2)
    freqs = met_to_freq(mels)

    return np.floor((FFT_size + 1) / sample_rate * freqs).astype(int), freqs

# After we have the filter points, we construct the filters.


def get_filters(filter_points, FFT_size):
    filters = np.zeros((len(filter_points)-2, int(FFT_size/2+1)))

    for n in range(len(filter_points)-2):
        filters[n, filter_points[n]: filter_points[n + 1]
                ] = np.linspace(0, 1, filter_points[n + 1] - filter_points[n])
        filters[n, filter_points[n + 1]: filter_points[n + 2]
                ] = np.linspace(1, 0, filter_points[n + 2] - filter_points[n + 1])

    return filters


# We will use the DCT-III. This type of DCT will extract high frequency and low frequency changes in the the signal
def dct(dct_filter_num, filter_len):
    basis = np.empty((dct_filter_num, filter_len))
    basis[0, :] = 1.0 / np.sqrt(filter_len)

    samples = np.arange(1, 2 * filter_len, 2) * np.pi / (2.0 * filter_len)

    for i in range(1, dct_filter_num):
        basis[i, :] = np.cos(i * samples) * np.sqrt(2.0 / filter_len)

    return basis


def test_model():

    audio_path = "voice_password\\static\\assets\\recorded_audio\\recordedAudio.wav"
    modelpath = "voice_password\\static\\assets\\trained_models\\"

    gmm_files = [os.path.join(modelpath, fname) for fname in
                 os.listdir(modelpath) if fname.endswith('.gmm')]

    # Load the Gaussian gender Models
    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    speakers = [fname.split("\\")[-1].split(".gmm")[0] for fname
                in gmm_files]

    sr, audio = read(audio_path)

    vector = extract_features(audio, sr)
    log_likelihood = np.zeros(len(models))

    for i in range(len(models)):
        print(models)
        gmm = models[i]  # checking with each model one by one
        scores = np.array(gmm.score(vector))
        log_likelihood[i] = scores.sum()

    winner = np.argmax(log_likelihood)
    print("\tdetected as - ", speakers[winner])
    time.sleep(1.0)

    return speakers[winner]
