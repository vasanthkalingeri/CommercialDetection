import pylab
from scipy.io import wavfile
import numpy as np
import os
import sys

FREQ = 44100
WINDOW_SIZE = 4096
OVERLAP_RATIO = 0.9
STORE = "audio.csv"
OUTPUT = "output.txt"
NEIGHBOURS = 10 #No of neighbours to consider for smoothening

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
    del plot
#    pylab.show()
#    pylab.savefig("test.png")
    return [Pxx, t, freqs]

def derivative(values):
    
    n = len(values)
    error = np.array([0]*(n - 1))
    for i in range(1, n):
        diff = np.abs(values[i] - values[i - 1])
        error[i - 1] = diff
    return error

def write(array, filename=STORE):
    
    """Writes array into a csv file"""
    
    f = open(filename, "w")
    for i in range(len(array[-1])):
        s = ""
        for j in range(len(array)):
            s += str(array[j][i]) + ","
        s = s[:-1] #Remove the last comma
        s += "\n" #Add new line instead
        f.write(s)
    f.close()

def get_time_string(t):
    
    time_string = []
    for i in t:
        m, s = divmod(i, 60)
        h, m = divmod(m, 60)
        time_string.append(str(int(h)) + ":" + str(int(m)) + ":" + str(int(s)))# * 100) / 100.0))
    return time_string

def smoothen(array, neighbours=NEIGHBOURS):
    
    n = np.shape(array)[0]
    temp_array = np.copy(array)
    for i in xrange(n - neighbours):
        value = np.mean(temp_array[i:i+neighbours])
        array[i:i+neighbours] = np.array([value]*neighbours)
    return array

def write_output(parameters):
    
    time_string = parameters[0]
    features = parameters[1]
    
    errors = features #For now we only have one feature
    repeated = 0
    splits = [time_string[0]]
    for i in xrange(np.shape(errors)[0]):
        if (errors[i] < 5):
            repeated += 1
        else:
            repeated = 0
        if time_string[i] != splits[-1] and repeated >= (NEIGHBOURS / 2):
            splits.append(time_string[i])
    
    f = open(OUTPUT, "w")
    s = "\n".join(splits)
    f.write(s)
    f.close()
    
def get_splits(data, t, f):
    
    n = np.shape(t)[0] - 1
    values = np.array([0]*(n - 1))
    for i in xrange(1, n):
        diff = np.sum(np.abs(data[:, i] - data[:, i - 1]))
        values[i - 1] = diff
    
    #First derivative of errors
    error = derivative(values)
    
    #Second derivative of errors
    serror = derivative(error)
    
    #We smoothen it out
    serror = smoothen(serror)
    time_string = get_time_string(t)
    
    write_output([time_string, serror])
    print "Done writing the output!!"
    write([time_string, values, serror]) #First parameter is time always

def main():
    
    Pxx, t, freqs = plot_spectrogram(sys.argv[1])    
    get_splits(Pxx, t, freqs)

main()
