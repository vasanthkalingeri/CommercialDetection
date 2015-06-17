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

    def find_commercial(self, start, span=VIDEO_SPAN):
        
#        print timeFunc.get_time_string(start), "....."
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
        
#        times = DetectSilence(TEMP_AUDIO).get_times()
#        print times
#        assert False
        
        times =['00:00:19', '00:00:20', '00:00:21', '00:00:22', '00:00:23', '00:00:24', '00:00:25', '00:00:26', '00:00:27', '00:00:28', '00:00:29', '00:00:30', '00:00:31', '00:00:32', '00:00:33', '00:00:34', '00:00:35', '00:00:36', '00:00:37', '00:00:38', '00:00:39', '00:00:40', '00:00:41', '00:00:42', '00:00:43', '00:00:44', '00:00:45', '00:00:46', '00:00:47', '00:00:48', '00:00:49', '00:01:19', '00:01:49', '00:01:50', '00:01:51', '00:01:52', '00:01:53', '00:01:54', '00:02:24', '00:02:25', '00:03:03']
        
#        times = ['00:00:19', '00:00:20', '00:00:21', '00:00:22', '00:00:23', '00:00:24', '00:00:25', '00:00:26', '00:00:27', '00:00:28', '00:00:29', '00:00:30', '00:00:31', '00:00:32', '00:00:33', '00:00:34', '00:00:35', '00:00:36', '00:00:37', '00:00:38', '00:00:39', '00:00:40', '00:00:41', '00:00:42', '00:00:43', '00:00:44', '00:00:45', '00:00:46', '00:00:47', '00:00:48', '00:00:49', '00:01:19', '00:01:49', '00:01:50', '00:01:51', '00:01:52', '00:01:53', '00:01:54', '00:02:24', '00:02:25', '00:02:38', '00:02:41', '00:03:03', '00:03:13', '00:03:21']#For shottest.mpg

        times = [timeFunc.get_seconds(i) for i in times]
        times.append(self.duration)
        i = 0
        end = 0
        name = UNCLASSIFIED_CONTENT
        silence = False
        sil_start = 0
        print timeFunc.get_time_string(0), timeFunc.get_time_string(times[0]), UNCLASSIFIED_CONTENT
        while i < len(times) - 1:
            div = (times[i] + times[i + 1]) / 2 #This eliminates errors due to fade in/out of commercials
            if times[i + 1] - times[i] > 1:
                #If not consequtive blocks of silence

                if silence is True:#Was silent before
                    print timeFunc.get_time_string(sil_start), timeFunc.get_time_string(times[i]), SILENCE
                    silence = False                  
                
                end, res = self.find_commercial(div)
                if len(res) != 0:#Ad was detected
                    start = res[0]
                    name = res[1]
                else:
                    start = times[i]
                    name = UNCLASSIFIED_CONTENT
    #                LabelsFile().write_labels(TEMP_FILE, [start, end, name])
                print timeFunc.get_time_string(times[i]), timeFunc.get_time_string(times[i+1]), name
            else:
                #Consequtive blocks of silence
                if silence is False:
                    sil_start = times[i]
                    silence = True
            i += 1
                
#    def __del__(self):
#        
#        os.remove(TEMP_AUDIO)
                
def test():
    
    recog = Recognize("../data/shottest.mpg")
    recog.recognize()

test()

