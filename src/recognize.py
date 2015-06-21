from dejavu.recognize import FileRecognizer, DataRecognizer
import os
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
        print times
        
        #For testing with shot_det.mpg
#        times = ['00:00:37', '00:00:38', '00:00:52', '00:00:53', '00:01:08', '00:01:38', '00:02:08', '00:02:09', '00:02:19', '00:02:22', '00:02:25', '00:02:26', '00:02:27', '00:02:28', '00:02:29', '00:02:30', '00:02:31', '00:02:32', '00:02:33', '00:02:48', '00:02:49', '00:02:53', '00:02:54', '00:02:55', '00:02:56', '00:02:57', '00:03:10', '00:03:11', '00:03:15', '00:03:17', '00:03:18', '00:03:20', '00:03:21', '00:03:22', '00:03:23', '00:03:24', '00:03:25', '00:03:27', '00:03:28', '00:03:29', '00:03:31', '00:03:32', '00:03:33', '00:03:36', '00:03:38', '00:03:39', '00:03:44', '00:03:46', '00:03:47', '00:03:48', '00:04:49', '00:04:50', '00:05:05', '00:05:34', '00:05:35', '00:05:36', '00:05:39', '00:05:41', '00:05:42', '00:05:48', '00:05:49', '00:05:54', '00:05:55', '00:05:58', '00:05:59', '00:06:03', '00:06:04', '00:06:05', '00:06:20', '00:06:21', '00:06:22', '00:06:23', '00:06:24', '00:06:25', '00:06:55', '00:07:00', '00:07:01', '00:07:02', '00:07:11', '00:07:18', '00:07:19', '00:07:27', '00:07:28', '00:07:34', '00:07:38', '00:07:39', '00:07:40', '00:07:41', '00:07:42', '00:07:44', '00:07:49', '00:07:53', '00:07:56', '00:08:00', '00:08:02', '00:08:04', '00:08:05', '00:08:08', '00:08:09', '00:08:11', '00:08:38', '00:08:40', '00:08:43', '00:08:44', '00:08:46', '00:08:51', '00:08:53', '00:08:54', '00:08:56', '00:08:57']
#        ad_times = [38, 53, 67, 99, 129, 288, 304, 334, 365, 384]
        
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
        ad = False
        while i < len(times) - 1:
            
#            #Pretty output
            sys.stdout.write('\r')
            sys.stdout.write("%d cuts analyzed " % (i + 1))
            sys.stdout.flush()
            
            div = (times[i] + times[i + 1]) / 2 #This eliminates errors due to fade in/out of commercials
            
            if ((ad is True) and times[i] >= times[i + 1]): #Skip the shot change detected in an ad
                times[i + 1] = times[i]
                i += 1
                print "Skipping stuff..."
                continue

            if (times[i + 1] - times[i] > 1):
                #If not consequtive blocks of silence

                if silence is True:#Was silent before
                    labels.write_labels([sil_start, times[i], SILENCE])
#                    print timeFunc.get_time_string(sil_start), timeFunc.get_time_string(times[i]), SILENCE
                    silence = False                  
                
                end, res = self.find_commercial(div)
                if len(res) != 0:#Ad was detected
                    start = res[0]
                    name = res[1]
                    times[i] = start
                    times[i + 1] = end
                    ad = True
                else:
                    start = times[i]
                    ad = False
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
        
        print "Removing the audio generated for the video.."
        os.remove(TEMP_AUDIO)
                
#def test():
#    
#    recog = Recognize("../data/shot_det.mpg")
#    recog.recognize()

#test()

