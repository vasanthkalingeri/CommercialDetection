import os
from constants import *

def get_time_string(tsecs):
    
    m, s = divmod(tsecs, 60)
    h, m = divmod(m, 60)
    time_string = str(int(h)) + ":" + str(int(m)) + ":" + str(int(s))
    return time_string

def get_seconds(tstring):
    
    form = tstring.count(":")# to check if h:m:s format or m:s format
    tstring = tstring.strip()
    time = tstring.split(":")
    time = [int(i) for i in time]
    secs = 0
    for i in range(form + 1):
        secs += time[i] * (60 ** (form - i))
    return secs

def get_delta_string(t1str, t2str):
    
    t1str = t1str.strip(" ")
    t2str = t2str.strip(" ")
    s1 = get_seconds(t1str)
    s2 = get_seconds(t2str)
    delta = s2 - s1
    return get_time_string(delta)

def read_lables(filename):
    
    with open(filename) as fd:
        for line in fd:
            line = line.split("=")
            line = [i.strip() for i in line]
            time = line[0].split("-")
            time = [i.strip(" ") for i in time]
            delta_str = get_delta_string(time[0], time[1])
            name = line[-1].strip()
            yield [time[0], name, delta_str]

def build_db(label_name, video_name):
    
    labels = read_lables(label_name)
    f = open(DBNAME, "a")
    filename = len(os.listdir(DB_FOLDER)) + 1 #Number of files in the directory + 1
    for data in labels:
        start = data[0]
        name = data[1]
        duration = data[2]
        path = DB_FOLDER + str(filename) + ".mpg"
        #Create a file in the db folder
        os.system("ffmpeg -ss " + start + " -i " + video_name + " -t " + duration + " -acodec copy -vcodec copy " + path)
        #Create a corresponding entry in the csv file
        s = ",".join(data[1:])
        s = s + "," + path + ",yes\n" #Check verified to be true since human tagged
        f.write(s)
        filename += 1
            
def test():
    
    build_db("labels", "test.mpg")    

test()
