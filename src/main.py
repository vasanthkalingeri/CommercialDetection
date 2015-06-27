from recognize import Recognize
from generate import Generate
import sys
import ffmpeg
import os
from constants import *

if sys.argv[1] == "-r":
    recog = Recognize(sys.argv[2])
    recog.recognize()

elif sys.argv[1] == "-g":
    gen = Generate(sys.argv[2], sys.argv[3])
    gen.run()

elif sys.argv[1] == "-l":

    global WEB_VIDEO_NAME
    video_name = sys.argv[2]
    ffmpeg.convert_video(video_name)
    name, extension = video_name[-5:].split('.')
    name = video_name.split('/')[-1]
    name = name[:-len(extension)-1]
    
    os.system("mv " + name + '.webm ' + 'web/output/static/output/out1.webm')
    WEB_VIDEO_NAME = name
    os.system('python web/manage.py runserver')
    
