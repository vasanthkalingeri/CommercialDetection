from dejavu.recognize import DataRecognizer, FileRecognizer
import os
import subprocess
import timeFunc
from constants import *
import ffmpeg
from dejavu import Dejavu, decoder
from scipy.io import wavfile

class Recognize(object):
    
    def __init__(self, video_name):
        
        self.video_name = video_name
        self.djv = Dejavu(CONFIG)
        
        #We create the audio for the video, extract the frames and delete the audio created
        ffmpeg.create_audio(self.video_name, TEMP_AUDIO)
        self.frames, self.Fs, file_hash = decoder.read(self.video_name)
        self.Fs = 44100
#        self.clean()

    def get_line(self, filename, index):
        
        f = open(filename)
        i = 0
        for line in f:
            if i == index:
                return line
            i += 1
        return -1

    def clean(self):
        
        #removes the temp files that were created
        os.remove(TEMP_AUDIO)
#        os.remove(TEMP_VIDEO)
            
    def recognize_audio(self, start, span=VIDEO_SPAN):
        
        """Recognize the audio between start and end
           start = duration in seconds from the start of the video(Use timeFunc.get_seconds() if in h:m:s format)
        """
        
        print timeFunc.get_time_string(start), "COMPLETE"
        song = self.djv.recognize(DataRecognizer, self.frames[0][start*self.Fs:(start+span)*self.Fs])
#        song = self.djv.recognize(FileRecognizer, self.video_name)
        print song
        if song[DJV_CONFIDENCE] >= CONFIDENCE_THRESH:
            #obtain the start of the commercial
            start -= song[DJV_OFFSET]
            start = int(start)
            
            #Read the database to obtain the end time of the commercial
            index = int(song[DJV_SONG_NAME]) #This is the line containing the db details
            line = self.get_line(DBNAME, index)
            line = line.split(",")
            print line
            
            name = line[0]
            duration = line[1]
            duration = timeFunc.get_seconds(duration)
            print duration
            verified = line[-1]
            print type(start)
            print type(duration)
            end = start + duration
                
            f = open(OUTPUT, "a")
            s = timeFunc.get_time_string(start) + " - " + timeFunc.get_time_string(end) + " = " + name 
            if verified == DB_UNCLASSIFIED: #Has not been verified in the database
                s += DB_UNCLASSIFIED
            else:
                s += DB_CLASSIFIED
            s += "\n"
            f.write(s)
            f.close()
            return (duration + 1)
        else:
            return VIDEO_GAP
    
    def recognize(self):
        
        #First we obtain the audio of the entire video
        duration = len(self.frames[0]) / (self.Fs*1.0)
        duration = int(duration)
        print duration, self.Fs, len(self.frames)
        base = 0
        while base < duration:
            print base
            base += self.recognize_audio(base)
    
def test():
    
    recog = Recognize("../data/shottest.mpg")
    recog.recognize()

test()
