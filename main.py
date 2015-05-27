import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as pylab
from scipy.io import wavfile
import numpy as np
import os
import sys
from constants import *
import detect
import os
import cv2


def get_time_string(tsecs):
    
    m, s = divmod(tsecs, 60)
    h, m = divmod(m, 60)
    time_string = str(int(h)) + ":" + str(int(m)) + ":" + str(int(s))
    return time_string

def write_output(time_splits):
    
    base = 0
    f = open(OUTPUT, 'w')
    for split in time_splits:
        delta = split - base
        base = split
        s = get_time_string(split) + " = "
        if delta < TIME_THRESH:
            s += "Commercial"
        else:
            s += "TV"
        s += "\n"
        f.write(s)
    f.close()

def analyze_spectrogram(filename, wsize=WINDOW_SIZE, fs=FREQ, overlap=OVERLAP_RATIO):

    fs, frames = wavfile.read(filename)
    channels = [
        np.array(frames[:, 0]),
        np.array(frames[:, 1])
    ]
    
    duration = int(len(channels[0]) / (FREQ * 1.0))
    print duration
    time_splits = []
    for i in xrange(duration / 2):
        start = i*(FREQ)*2
        
        # generate specgram
        pylab.axis("off")
        Pxx, freqs, t, plot = pylab.specgram(
            channels[0][start:(FREQ*2) + start],
            NFFT=wsize, 
            Fs=fs*20, 
            detrend=pylab.detrend_none,
            window=pylab.window_hanning,
            noverlap=int(wsize * overlap),
            cmap='Greys',
            pad_to=FREQ)
        
        if SAVE_IMAGES:
            pylab.savefig(SPEC_FOLDER + str(i) + ".png", bbox_inches='tight', pad_inches=0)

        pylab.savefig(TEMP_FILE, bbox_inches='tight', pad_inches=0)
        img = cv2.imread(TEMP_FILE)
        os.remove(TEMP_FILE)
        if detect.analyze(img):
            print "Found a split at", get_time_string(i * 2)
            time_splits.append(i * 2)
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*(i / (2 * duration)), i))
        sys.stdout.flush()
    
    return time_splits

def generate_audio(filename):

    print "Generating audio.."
    os.system("ffmpeg -i "+ filename +" -ab 160k -ac 2 -ar 44100 -vn " + AUDIO_FILE)    
    print "Done generating"
    
def main():
    
    generate_audio(sys.argv[1])
    print "Analyzing audio"
    time_splits = analyze_spectrogram(AUDIO_FILE)  
    write_output(time_splits) 
    
main()
