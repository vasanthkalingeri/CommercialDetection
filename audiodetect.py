import numpy as np
from scipy.io import wavfile
import timeFunc
import hickle
import matplotlib.pyplot as plt
import cv2

def spectral_centroid(x, samplerate=44100):

    magnitudes = np.abs(np.fft.rfft(x)) # magnitudes of positive frequencies
    length = len(x)
    print len(magnitudes)
    freqs = np.abs(np.fft.fftfreq(length, 1.0/samplerate)[:length//2+1]) # positive frequencies
    return np.sum(magnitudes*freqs) / np.sum(magnitudes) # return weighted mean

def get_data(audio_name, window=1, overlap=0.3):

    fs, frames = wavfile.read(audio_name)
    start = 0
    i = window
    m = 0
    X = np.array([])
    while ((i*fs) < len(frames)):
        print timeFunc.get_time_string(i)
        end = start + int(fs * window)
        x = np.array(frames[start:end]) + 0.0001#To remove any zero errors
        print x.shape, start, end
        print end-start
        magnitudes = np.abs(np.fft.rfft(x))[:fs / 4] #Only these are used for similarity measure
        X = np.append(X, magnitudes)
        start += int(fs * (1 - overlap) * window)
        i += window
        m += 1
    print X.shape
    print m, fs/4
    X = np.reshape(X, (m, len(magnitudes)))
    hickle.dump(X, 'dat.hkl', mode='w')
    return [fs, X]

def cos_distance(vector1, vector2):
    
    dot_prod = np.dot(vector1, vector2)
    mag_vec1 = np.linalg.norm(vector1)
    mag_vec2 = np.linalg.norm(vector2)
    return dot_prod / ((mag_vec1) * (mag_vec2))

def kernel(size=64):
    
    cboard = np.array([[1, -1], [-1, 1]])
    i = cboard.shape[0]
    while i < size:
        print i
        I = np.ones((i,i), dtype=np.dtype('b')) #Take only one byter per element
        cboard = np.kron(cboard, I)
        i = cboard.shape[0]
        
    return cboard    

def analyze(audio_name, skip = 2):
    
#    fs, X = get_data(audio_name, window=0.01)
    X = hickle.load("dat.hkl")
    print "Done loading"
    m = X.shape[0]
    print m
    m /= (skip)
    print m
    S = np.zeros((m, m), dtype=np.float32)
    i = 0
    lag = 256 #this is the width of the kernel
    x = y = 0
    while x < m:
        print x,y,m
        i = skip*x
        y = x
        while ((y - x) <= lag) and y < m: #Require only these values
            j = skip*y
            S[x,y] = cos_distance(X[i, :], X[j, :])
            S[y,x] = S[x,y]
            y += 1
#            j += skip
#        i += skip
        x += 1
    print x, m
    hickle.dump(S, 'board.hkl', mode='w')
    return S

def save_img(S):
    
    S = hickle.load('board.hkl')
    S *= 255
    S = np.fliplr(S)
    print "Loaded the image"
    cv2.imwrite("board.png", S)

def pad_zero(vector, pad_width, iaxis, kwargs):

    vector[:pad_width[0]] = 0
    vector[-pad_width[1]:] = 0
    return vector

def convolve(S, k):
    
    S = hickle.load('board.hkl')
    k = kernel(16)
    #First we zero pad S
    S = np.lib.pad(S, k.shape[0] - 1, pad_zero)
    print k.shape
    lag = k.shape[0]
    m = S.shape[0]
    #Now we obtain the matrix and find the novelty
    i = m - lag
    j = 0
    novel = np.zeros((m, ))
    while (i > lag) and (j <= (m - lag)):
        arr = np.copy(S[i:i+lag, j:j+lag])
        novel[j] = np.sum(np.multiply(arr, k))
        print i,i+lag, j, j+lag
        j += 1
        i -= 1
    novel = novel[lag:m-lag]
    print novel
    hickle.dump(novel, 'newnovel.hkl', mode="w")
    return novel
       
def novelty():

    novel = hickle.load('newnovel.hkl')
    novel = novel[2980:3300]
    plt.plot(novel)
    plt.show()    

def test():
    
    print "running"
#    S = analyze("aud_s.wav")
#    print "Saving image"
#    save_img(None)
#    print "Finding novelty"
#    convolve(None, None)
    novelty()
    print "Done with all"
    
test()
