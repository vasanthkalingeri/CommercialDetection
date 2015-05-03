# numerical processing and scientific libraries
import numpy as np
import scipy

# signal processing
from scipy.io                     import wavfile as wav
from scipy                        import stats, signal
from scipy.fftpack                import fft

from scipy.signal                 import lfilter, hamming
from scipy.fftpack.realtransforms import dct
from scikits.talkbox              import segment_axis
from scikits.talkbox.features     import mfcc
from numpy.lib import stride_tricks
from matplotlib import pyplot as plt

# general purpose
import collections

import cPickle as pickle
DATA_FILE = "freq.dat"

def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):

    """ short time fourier transform of audio signal """
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))
    
    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.floor(frameSize/2.0)), sig)    
    # cols for windowing
    cols = np.ceil( (len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))
    
    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize), strides=(samples.strides[0]*hopSize, samples.strides[0])).copy()
    frames *= win
    
    return np.fft.rfft(frames)    
    

def logscale_spec(spec, sr=44100, factor=20.):

    """ scale frequency axis logarithmically """    
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins-1)/max(scale)
    scale = np.unique(np.round(scale))
    
    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale)-1:
            newspec[:,i] = np.sum(spec[:,scale[i]:], axis=1)
        else:        
            newspec[:,i] = np.sum(spec[:,scale[i]:scale[i+1]], axis=1)
    
    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins*2, 1./sr)[:freqbins+1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale)-1:
            freqs += [np.mean(allfreqs[scale[i]:])]
        else:
            freqs += [np.mean(allfreqs[scale[i]:scale[i+1]])]
    
    return newspec, freqs

def plotstft(audiopath, binsize=2**10, plotpath=None, colormap="jet"):
    
    """ plot spectrogram"""
    
    
    samplerate, samples = wav.read(audiopath)
    
    s = stft(samples, binsize)
    
    
    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20.*np.log10(np.abs(sshow)/10e-6) # amplitude to decibel

    timebins, freqbins = np.shape(ims)
    
    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins-1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins-1, 5))
    xtick = ["%s:%s"%(divmod(int(l), 60)[0], divmod(int(l), 60)[1]) for l in ((xlocs*len(samples)/timebins)+(0.5*binsize))/samplerate]
    plt.xticks(xlocs, xtick)
    ylocs = np.int16(np.round(np.linspace(0, freqbins-1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])
    
    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()
    plt.clf()
    return [ims, timebins, freqbins]

def find_times(ims, timebins, freqbins):    

    global SAMPLE_RATE
    
    count = []     
    for i in range(timebins):
        #Count how blue the region is, the bluer the region in the spectrograph, lower are the values
        c = 0
        for j in range(freqbins):
            if ims[i][j] < 135:
                c += 1
        count.append(c)
    for i in range(timebins):
        print count[i], i
    
def main():
    
    ims, timebins, freqbins = plotstft("audio.wav")
    find_times(ims, timebins, freqbins)
    
main()
