from dejavu.recognize import FileRecognizer, DataRecognizer
import os
import subprocess
import timeFunc
from constants import *
import ffmpeg
from dejavu import Dejavu, decoder
import numpy as np
from audiodetect import DetectSilence

class Recognize(object):
    
    """
        This class runs the audio fingerprinting algorithm to find matches of commercials in the audio.
        First detects regions of silence and does match finding only around the regions of silence.
        
    """
    def __init__(self, video_name):
        
        self.video_name = video_name
        self.djv = Dejavu(CONFIG)
        
        #We create the audio of the video given to us
#        ffmpeg.create_audio(self.video_name, TEMP_AUDIO)
        self.frames, self.Fs, hash_val = decoder.read(TEMP_AUDIO)
        self.frames = self.frames[0] #Since we always create single channel audio
        self.duration = int(self.frames.shape[0] / (self.Fs*1.0)) #Duration of the entire video in seconds
        
    def get_line(self, filename, index):
        
        f = open(filename)
        i = 0
        for line in f:
            if i == index:
                return line
            i += 1
        return -1

    def find_commercial(self, start, span=VIDEO_SPAN):
        
        print timeFunc.get_time_string(start), "COMPLETE"
        data = np.copy(self.frames[start*self.Fs:(start+span)*self.Fs])
        print (start+span)
        song = self.djv.recognize(DataRecognizer, [data])
        if song is None:
            return [VIDEO_GAP, False]
        if song[DJV_CONFIDENCE] >= CONFIDENCE_THRESH:
            #obtain the start of the commercial
            start -= song[DJV_OFFSET]
            start = int(start)
            
            #Read the database to obtain the end time of the commercial
            index = int(song[DJV_SONG_NAME]) #This is the line containing the db details
            line = self.get_line(DBNAME, index)
            line = line.split(",")
            name = line[0]
            duration = line[1]
            duration = timeFunc.get_seconds(duration)
            
            if duration < song[DJV_OFFSET] or song[DJV_OFFSET] < 0:
                #Offset can never be greater than duration of detected commercial
                return [VIDEO_GAP, False]
            
            verified = line[-1]
            end = start + duration
                
            f = open(OUTPUT, "a")
            s = timeFunc.get_time_string(start) + " - " + timeFunc.get_time_string(end) + " = " + name 
            if verified == DB_UNCLASSIFIED: #Has not been verified in the database
                s += " " + DB_UNCLASSIFIED
            else:
                s += " " + DB_CLASSIFIED
            s += "\n"
            f.write(s)
            f.close()
            return [(start + duration), True]
        else:
            return [VIDEO_GAP, False]
            
    def recognize(self):
        
        #Generates temp.mpg which is the temp video file and temp.wav, its corresponding audio file
        
#        times = DetectSilence(TEMP_AUDIO).get_times()
#        print times
        times = ['00:00:49', '00:01:19', '00:01:54', '00:02:25', '00:02:38', '00:02:41', '00:03:03', '00:03:13', '00:03:21'] #For shottest.mpg
        times = [timeFunc.get_seconds(i) for i in times]
        i = 0
        while i < len(times):
            start = times[i]
            end, res = self.find_commercial(start)
            i += 1
            #If its an ad, we skip through to the point where the ad ends
#            while (res is True) and (end > times[i]):
#                i += 1
                
#    def __del__(self):
#        
#        os.remove(TEMP_AUDIO)
                
def test():
    
    recog = Recognize("../data/shottest.mpg")
    recog.recognize()

test()

