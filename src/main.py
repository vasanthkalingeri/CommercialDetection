from recognize import Recognize
from generate import Generate
import sys
import ffmpeg
import os
from constants import *

"""This is the main driver program"""

if len(sys.argv) == 1:
    
    print "Format is \n python main.py -[r/g/l] [labels_file] video_name"
    
elif sys.argv[1] == "-r":

    print "Recognizing...", sys.argv[2]
    recog = Recognize(sys.argv[2])
    recog.recognize()

elif sys.argv[1] == "-g":

    print "Generating for video", sys.argv[3], "with labels file as", sys.argv[2]  
    gen = Generate(sys.argv[2], sys.argv[3])
    gen.run()

elif sys.argv[1] == "-l":

    print "Learning for video", sys.argv[3]
    global WEB_VIDEO_NAME
    video_name = sys.argv[3]
    ffmpeg.convert_video(video_name)
    name, extension = video_name[-5:].split('.')
    name = video_name.split('/')[-1]
    name = name[:-len(extension)-1]
    os.system("mv " + name + '.webm ' + 'web/output/static/output/out2.webm')
    print "Go to the URL to edit output.txt"
