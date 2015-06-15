import numpy as np
from scipy.io import wavfile
import timeFunc
import hickle
from constants import *

class DetectSilence(object):
    
    def __init__(self, audio_name):
        
        self.audio_name = audio_name
        self.X = np.array([])
        self.Fs = None
                
    def get_data(self, window=WINDOW_SIZE, overlap=0):

        """
            Gets the freq region of data
            audio_name = name of the audio file
            Window = size of the window in seconds, by default it creates a window of 2 milliseconds
            Overlap = ratio of overlap between frames
        """
        self.Fs, frames = wavfile.read(self.audio_name)
        start = 0
        i = window
        m = 0
        while ((i*self.Fs) < len(frames)):
            print timeFunc.get_time_string(i)
            end = start + int(self.Fs * window)
            x = np.array(frames[start:end]) + 0.0001#To remove any zero errors
            print x.shape, start, end
            print end-start
            magnitudes = np.abs(np.fft.rfft(x))[:self.Fs / 4] #Only these are used for similarity measure
            self.X = np.append(self.X, magnitudes)
            start += int(self.Fs * (1 - overlap) * window)
            i += window
            m += 1
        print self.X.shape
        print m, self.Fs/4
        self.X = np.reshape(self.X, (m, len(magnitudes)))
#        hickle.dump(self.X, '../data/newdat.hkl', mode='w')

    def detect(self):
        
        #Each step of X is 10ms
        m,n= self.X.shape
        print m, n
        
        freqs = np.abs(np.fft.fftfreq(n, 1.0/44100))
        times = []
        for i in range(m):
            magnitudes = self.X[i, :]
            val = (np.min(magnitudes) + np.max(magnitudes)) / np.var(magnitudes)
            val *= 100
            print timeFunc.get_time_string(i * WINDOW_SIZE), val
            if val > 1:
                times.append(timeFunc.get_time_string(i * WINDOW_SIZE))

        j = 0
        while j < len(times) - 1:
            delta = timeFunc.get_delta_string(times[j], times[j + 1])
            delta = timeFunc.get_seconds(delta)
            if delta <= 1:
                times.remove(times[j])
            else:
                j += 1
        print times
    
    def run(self):
        
        self.get_data()
        self.detect()
            
def test():
    
    print "running"
    DetectSilence("../data/aud_s.wav").run()
    print "Done with all"
    
test()
