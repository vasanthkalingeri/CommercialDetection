import os
from constants import *
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
import timeFunc
import ffmpeg

config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "pass",
        "db": "dejavu"
    }
}

djv = Dejavu(config)

def read_lables(filename):
    
    with open(filename) as fd:
        for line in fd:
            line = line.split("=")
            line = [i.strip() for i in line]
            time = line[0].split("-")
            time = [i.strip(" ") for i in time]
            delta_str = timeFunc.get_delta_string(time[0], time[1])
            name = line[-1].strip()
            yield [time[0], name, delta_str]

def build_db(label_name, video_name, aud_ext=".wav", vid_ext=".mpg"):
    
    labels = read_lables(label_name)
    
    filename = len(os.listdir(DB_AUDIO)) + 1 #Number of files in the directory + 1
    if filename == 1:
        #Creating for the first time
        f = open(DBNAME, "w")
        f.write("name, duration, path, verified")
    else:
        #Already exists
        f = open(DBNAME, "a")
            
    for data in labels:
        start = data[0]
        name = data[1]
        duration = data[2]
        #Create a file in the db folder, audio and video are stored seperately 
        ffmpeg.create_video(start, duration, video_name, DB_VIDEO + str(filename) + vid_ext)
        ffmpeg.create_audio(DB_VIDEO + str(filename) + vid_ext, DB_AUDIO + str(filename) + aud_ext)
        #Create a corresponding entry in the csv file
        s = ",".join(data[1:])
        s = s + "," + DB_VIDEO + str(filename) + vid_ext + ",yes\n" #Check verified to be true since human tagged
        f.write(s)
        filename += 1

def fingerprint_db(aud_ext=".wav", no_proc=4):
    
    djv.fingerprint_directory(DB_AUDIO, [aud_ext], no_proc)

def test():
    
    build_db("labels_2015-04-28_0000_US_KABC", "2015-04-28_0000_US_KABC_Eyewitness_News_5PM.mpg")
    build_db("labels", "test.mpg") 

test()
