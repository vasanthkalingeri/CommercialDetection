import pylab
from scipy.io import wavfile
import numpy as np
import os

FREQ = 44100
WINDOW_SIZE = 4096
OVERLAP_RATIO = 0.9
STORE = "audio.dat"

def plot_spectrogram(filename, wsize=WINDOW_SIZE, fs=FREQ, overlap=OVERLAP_RATIO):

    fs, frames = wavfile.read(filename)
    channels = [
        np.array(frames[:, 0]),
        np.array(frames[:, 1])
    ]

    # generate specgram
    Pxx, freqs, t, plot = pylab.specgram(
        channels[0],
        NFFT=wsize, 
        Fs=fs, 
        detrend=pylab.detrend_none,
        window=pylab.window_hanning,
        noverlap=int(wsize * overlap))
#    pylab.show()
#    pylab.savefig("test.png")
    return [Pxx, t, freqs]

def get_splits(data, t, f):
    
    n = np.shape(t)[0] - 1
    values = np.array([0]*(n - 1))
    for i in xrange(1, n):
        diff = np.sum(np.abs(data[:, i] - data[:, i - 1]))
#        print diff, t[i]
        values[i - 1] = diff
    
    error = np.array([0]*(n - 1))
    for i in range(1, n - 1):
        diff = np.abs(values[i] - values[i - 1])
        print diff, t[i]
        error[i - 1] = diff
        
def main():
    
    Pxx, t, freqs = plot_spectrogram("aud.wav")    
    get_splits(Pxx, t, freqs)

main()
