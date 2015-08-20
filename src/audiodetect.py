import numpy as np
from scipy.io import wavfile
import timeFunc
#import hickle
from constants import *
import sys

class DetectSilence(object):
    
    def __init__(self, audio_name):
        
        self.audio_name = audio_name
        self.Fs = None
        self.times = []
        self.times_dic = {}
        self.X = None
        
    def get_data(self, window, overlap):

        """
            Gets the freq region of data
            audio_name = name of the audio file
            Window = size of the window in seconds, by default it creates a window of 2 milliseconds
            Overlap = ratio of overlap between frames
        """
        print
        print "Computing FFT..",
        self.Fs, frames = wavfile.read(self.audio_name)
        start = 0
        i = window
        m = int(len(frames) / (window * self.Fs)) # As (k + 1)*window*fs < len(frames)
        
        #Creating an empty X matrix
        n = np.fft.fftfreq(int(self.Fs*window))[: self.Fs // 2].shape[0] #Only real part
        n = n / 2 + 1 #Since we take only half of real part
        self.X = np.zeros((m, n), dtype=np.float32)
        
        k = 0
        print
        while ((i*self.Fs) < len(frames)):
            #Pretty output
            sys.stdout.write('\r')
            sys.stdout.write("%s done" % (timeFunc.get_time_string(i)))
            sys.stdout.flush()
            
            end = start + int(self.Fs * window)
            x = np.array(frames[start:end], dtype=np.float32) + 0.0000001#To remove any zero errors
            magnitudes = np.abs(np.fft.rfft(x))[:self.Fs / 4]
            self.X[k] = np.copy(magnitudes)
            start += int(self.Fs * (1 - overlap) * window)
            i += window
            k += 1
        print
        print "Done computing FFT !"
        print        
#        hickle.dump(self.X, '../data/newdat.hkl', mode='w')

    def detect(self):
        
#        self.X = hickle.load('../data/newdat.hkl')
        m,n= self.X.shape
        freqs = np.abs(np.fft.fftfreq(n, 1.0/44100))
        times = []
        print 
        print "Detecting video cuts..",
        print
        for i in range(m):
            magnitudes = self.X[i, :]
            val = (np.max(magnitudes) + np.min(magnitudes)) / (np.var(magnitudes))
            val *= 100
            
            #Pretty output
            sys.stdout.write('\r')
            sys.stdout.write("%s done" % (timeFunc.get_time_string(i * WINDOW_SIZE)))
            sys.stdout.flush()
            
            if val > 1:
                ts = timeFunc.get_time_string(i * WINDOW_SIZE)
                try:
                    self.times_dic[ts] += 1
                except:
                    self.times_dic[ts] = 0
        print
        j = 0
        times = self.times_dic.keys()
        times.sort
        for time in times:
            if self.times_dic[time] == 0: #Occurred only once, very low chances of it being valid
                del self.times_dic[time]
        self.times = self.times_dic.keys()
        self.times.sort()
        print "Video cuts detected !"
        print
    
    def get_times(self, window=WINDOW_SIZE, overlap=OVERLAP):
        
        self.get_data(window, overlap)
        self.detect()
        return self.times
#            
#def test():
#    
#    print "running"
#    print DetectSilence(TEMP_AUDIO).get_times()
#    print "Done with all"
#    
#test()
