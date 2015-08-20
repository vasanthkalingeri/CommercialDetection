"""
    This file deals with the detection of commercials in a given video
"""
from dejavu.recognize import FileRecognizer, DataRecognizer
import os
import timeFunc
from constants import *
import ffmpeg
from dejavu import Dejavu, decoder
import numpy as np
from fileHandler import LabelsFile, DatabaseFile
import sys
import mimetypes

class Recognize(object):
    
    """
        This class runs the audio fingerprinting algorithm to find matches of commercials in the audio.
    """

    def __init__(self, video_name):
        
        """
           Takes the video name. Creates a Dejavu object.
           Also obtains the duration and number of frames in the video.
        """
        
        file_type = mimetypes.guess_type(video_name)[0]
        
        if file_type[:3] != "vid":#The file is not a video file
            print "No video file found"
            raise Exception(INCORRECT_VIDEO_FILE_ERROR)
        
        self.video_name = video_name
        self.djv = Dejavu(CONFIG)
        
        #We create the audio of the video given to us
        ffmpeg.create_audio(self.video_name, TEMP_AUDIO)
        self.frames, self.Fs, hash_val = decoder.read(TEMP_AUDIO)
        self.frames = self.frames[0] #Since we always create single channel audio
        self.duration = int(self.frames.shape[0] / (self.Fs*1.0)) #Duration of the entire video in seconds
        
    def find_commercial(self, start, span=VIDEO_SPAN):
        
        """
            Uses audio fingerprinting to detect known commercials
            Returns:
                If commercial is detected it returns the following:
                    [end_time, [actual_start of commercial, duration of commercial]]
                If no commercial is found
                    [start(the value that was passed), []]
        """
        
        data = np.copy(self.frames[start*self.Fs:(start+span)*self.Fs]) #Obtain frames between the desired locations
        song = self.djv.recognize(DataRecognizer, [data]) #Call dejavu to audio fingerprint it and find a match
        
        if song is None:
            #No match was found in the db
            return [start, []] #We can safely skip
            
        if song[DJV_CONFIDENCE] >= CONFIDENCE_THRESH:
            #A high confidence match was found
            
            if song[DJV_OFFSET] < 0:
                #Offset can never be greater than duration of detected commercial
                return [start, []]
            
            #song[DJV_OFFSET] contains the time duration of the original song, which the segment matched
                            
            #obtain the start of the commercial
            start -= song[DJV_OFFSET]
            start = int(start)
            
            #Read the database to obtain the end time of the commercial
            #This is the line containing the db details
            #We subtract 1, since by default audio/ and video/ have .temp folder in them
            
            index = int(song[DJV_SONG_NAME]) - 1 
            
            #Obtain the name and duration of the detected segment
            name, duration = DatabaseFile(DBNAME).get_line(index)
            
            if duration < song[DJV_OFFSET]:
                #The offset where it is found cannot exceed the duration of the song
                return [start, []]
            
            end = start + duration
                      
            return [end, [start, name]]
        else:
            #A match was found, but not a confident match
            return [start, []]
            
    def recognize(self):
        
        labels = LabelsFile(outfile=OUTPUT) 
        print "Now detecting commercials.."
        i = 0
        prev = 0
        while i < self.duration:
            
            #Pretty printing
            remaining_time = self.duration - i
            sys.stdout.write('\r')
            sys.stdout.write("Duration of video pending analysis: %s" % timeFunc.get_time_string(remaining_time))
            sys.stdout.flush()
            
            next, data = self.find_commercial(i)
            
            #data is an empty list when there is no commercial            
            if len(data) != 0:
                #If commercial is detected
                start = data[0]
                name = data[1]
                i = next + (VIDEO_GAP / 2)
                
                #prev = the end time of the last add that was detected
                if (start - prev) >= VIDEO_SPAN:
                    #If greater than the amount to scan, has to be marked unclassified
                    labels.write_labels([timeFunc.get_time_string(prev), timeFunc.get_time_string(start), UNCLASSIFIED_CONTENT])
                else:
                    start = prev #We safely skip
                
                prev = next   
                
                #We mark the commercial detected
                labels.write_labels([timeFunc.get_time_string(start), timeFunc.get_time_string(next), name])                     
            
            else:
                #No commercial, proceed scanning
                i += VIDEO_GAP
        print
                
        if (self.duration - prev) > 1: #Atleast one second
            labels.write_labels([timeFunc.get_time_string(prev), timeFunc.get_time_string(self.duration), UNCLASSIFIED_CONTENT])
                                    
    def __del__(self):
        
        print "Removing the audio generated for the video.."
        os.remove(TEMP_AUDIO)
                
#def test():
#    
#    recog = Recognize("../data/shot_det.mpg")
#    recog.recognize()

#test()

