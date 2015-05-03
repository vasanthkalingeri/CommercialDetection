import pylab
from scipy.io import wavfile
import numpy as np

FREQ = 44100
WINDOW_SIZE = 4096
OVERLAP_RATIO = 0.5

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
    pylab.show()

def main():
    
    plot_spectrogram("audio.wav")

main()
