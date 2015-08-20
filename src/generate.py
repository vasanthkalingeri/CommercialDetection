"""
    This file deals with the generation of fingerprints and storing in the mysql db
"""

import os
from constants import *
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
import timeFunc
import ffmpeg
from fileHandler import LabelsFile
import mimetypes

class Generate(object):

    """
        Given a labelled output file and the corresponding video tags, extracts the commercial segments and fingerprints them.
    """

    def __init__(self, labels_fname, video_name):
        
        label_file_type = mimetypes.guess_type(labels_fname)[0]
        video_file_type = mimetypes.guess_type(video_name)[0]
        
        if label_file_type[:3] != "tex":
            #The file is not a labels file
            print "Incorrect label file"
            raise Exception(INCORRECT_LABEL_FILE_ERROR)
        
        if video_file_type[:3] != "vid":
            #The file is not a video file
            print "Incorrect video file"
            raise Exception(INCORRECT_VIDEO_FILE_ERROR)
            
        self.labels = LabelsFile(labels_fname)
        self.video_name = video_name
        self.djv = Dejavu(CONFIG)
        self.db_content = []
            
    def build_db(self, aud_ext=".wav", vid_ext=".mpg"):
        
        """
            Build a sql db with the commercials
        """
        
        #This returns the entire contents of the file, more about structure of return type in fileHandler.py
        labels = self.labels.read_lables()
        
        #Number of files in the directory + 1
        filename = len(os.listdir(DB_AUDIO)) + 1
        
        #Try reading contents from csv file, if it already exists
        try:
            #Already exists
            #We open and read the content first
            with open(DBNAME) as f:
                lines = f.readlines()
                self.db_content = [line.split(',')[1] for line in lines[1:]] #Only names of commercials
            f = open(DBNAME, "a")
            
        except:
            #Creating for the first time
            print "File does not exist so creating..."
            f = open(DBNAME, "w")
            f.write("name, duration, path\n")
        
        for data in labels:
            
            #Extracting based on structure of return type
            start = data[0]
            end = data[1]
            name = data[2]
            
            if self.db_content != [] and (name in self.db_content):
                print "Already Fingerprinted"
                continue

            duration = timeFunc.get_delta_string(start, end)
            
            #Create a file in the db folder, audio and video are stored seperately 
            ffmpeg.create_video(start, duration, self.video_name, DB_VIDEO + str(filename) + vid_ext)
            ffmpeg.create_audio(DB_VIDEO + str(filename) + vid_ext, DB_AUDIO + str(filename) + aud_ext)
            
            #Create a corresponding entry in the csv file
            s = ",".join([name, duration])
            s = s + "," + DB_VIDEO + str(filename) + vid_ext + "\n" #Check verified to be true since human tagged
            f.write(s)
            filename += 1

    def fingerprint_db(self, aud_ext=".wav", no_proc=1):

        #This fingerprints the entire directory
        self.djv.fingerprint_directory(DB_AUDIO, [aud_ext])
        
    def clean_db(self, aud_ext=".wav", vid_ext=".mpg"):
        
        choice = raw_input("Are you sure you want to remove all commercials in the database? (yes/no)")
        if choice == "yes":
            #Clear the mysql db
            self.djv.clear_data() 
            print "Cleaning database.."
            
            #Now we remove files from db/audio and db/video
            filename = len(os.listdir(DB_AUDIO)) + 1
            for i in range(1, filename):
                try:
                    os.remove(DB_AUDIO + str(i) + aud_ext)
                    os.remove(DB_VIDEO + str(i) + vid_ext)
                except:
                    print "File already removed, or you don't have permission"
                    
            os.remove(DBNAME)
            print "Database is empty"
        
    def run(self, aud_ext=".wav", vid_ext=".mpg"):
        
        self.build_db(aud_ext, vid_ext)
        self.fingerprint_db(aud_ext, vid_ext)
        
#def test():
    
#    gen = Generate("../data/labels_2015-04-28_0000_US_KABC", "../data/2015-04-28_0000_US_KABC_Eyewitness_News_5PM.mpg")
    
#    gen.run()
#    gen = Generate("../data/labels", "../data/shot_det.mpg") 
#    gen.run()
#    gen.clean_db()

#test()
