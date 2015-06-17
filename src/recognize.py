from dejavu.recognize import FileRecognizer, DataRecognizer
import os
import subprocess
import timeFunc
from constants import *
import ffmpeg
from dejavu import Dejavu, decoder
import numpy as np
from audiodetect import DetectSilence
from fileHandler import LabelsFile, DatabaseFile
import sys

class Recognize(object):
    
    """
        This class runs the audio fingerprinting algorithm to find matches of commercials in the audio.
        First detects regions of silence and does match finding only around the regions of silence.
        
    """
    def __init__(self, video_name):
        
        self.video_name = video_name
        self.djv = Dejavu(CONFIG)
        
        #We create the audio of the video given to us
        ffmpeg.create_audio(self.video_name, TEMP_AUDIO)
        self.frames, self.Fs, hash_val = decoder.read(TEMP_AUDIO)
        self.frames = self.frames[0] #Since we always create single channel audio
        self.duration = int(self.frames.shape[0] / (self.Fs*1.0)) #Duration of the entire video in seconds

    def find_commercial(self, start, span=VIDEO_SPAN):
        
        """Uses audio fingerprinting to detect known commercials"""
        
        data = np.copy(self.frames[start*self.Fs:(start+span)*self.Fs])
        song = self.djv.recognize(DataRecognizer, [data])
        if song is None:
            return [start, []] #We can safely skip
        if song[DJV_CONFIDENCE] >= CONFIDENCE_THRESH:

            if song[DJV_OFFSET] < 0:
                #Offset can never be greater than duration of detected commercial
                return [start, []]
                            
            #obtain the start of the commercial
            start -= song[DJV_OFFSET]
            start = int(start)
            
            #Read the database to obtain the end time of the commercial
            index = int(song[DJV_SONG_NAME]) #This is the line containing the db details
            name, duration, verified = DatabaseFile(DBNAME).get_line(index)
            
            if duration < song[DJV_OFFSET]:
                #The offset where it is found cannot exceed the duration of the song
                return [start, []]
            
            end = start + duration
                      
            return [end, [start, name]]
        else:
            return [start, []]
            
    def recognize(self):
        
        #Generates temp.mpg which is the temp video file and temp.wav, its corresponding audio file
        
        times = DetectSilence(TEMP_AUDIO).get_times()
                
        
        times = [timeFunc.get_seconds(i) for i in times]
        times.append(self.duration)
        i = 0
        end = 0
        name = UNCLASSIFIED_CONTENT
        silence = False
        sil_start = 0
        labels = LabelsFile(outfile=OUTPUT)
        labels.write_labels([0, times[0], UNCLASSIFIED_CONTENT])
#        print timeFunc.get_time_string(0), timeFunc.get_time_string(times[0]), UNCLASSIFIED_CONTENT
        print
        print len(times) - 1, "cuts to be analyed"
        print "Now Finding commercials..",
        print
        while i < len(times) - 1:
            
            #Pretty output
            sys.stdout.write('\r')
            sys.stdout.write("%d cuts analyzed " % (i + 1))
            sys.stdout.flush()
            
            div = (times[i] + times[i + 1]) / 2 #This eliminates errors due to fade in/out of commercials
            
            if times[i + 1] - times[i] > 1:
                #If not consequtive blocks of silence

                if silence is True:#Was silent before
                    labels.write_labels([sil_start, times[i], SILENCE])
#                    print timeFunc.get_time_string(sil_start), timeFunc.get_time_string(times[i]), SILENCE
                    silence = False                  
                
                end, res = self.find_commercial(div)
                if len(res) != 0:#Ad was detected
                    start = res[0]
                    name = res[1]
                else:
                    start = times[i]
                    name = UNCLASSIFIED_CONTENT
                    
                labels.write_labels([times[i], times[i+1], name])
#                print timeFunc.get_time_string(times[i]), timeFunc.get_time_string(times[i+1]), name
            else:
                #Consequtive blocks of silence
                if silence is False:
                    sil_start = times[i]
                    silence = True
            i += 1
        print
        print "Done finding known commercials, output written into", OUTPUT
        print
                
    def __del__(self):
        
        os.remove(TEMP_AUDIO)
                
def test():
    
    recog = Recognize("../data/shottest.mpg")
    recog.recognize()

test()

