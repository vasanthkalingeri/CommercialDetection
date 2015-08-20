from recognize import Recognize
from generate import Generate
import sys
import ffmpeg
import os
from constants import *
from errorCodes import *
import mimetypes

"""This is the main driver program"""

def main():

    if len(sys.argv) == 1:
        
        print "Format is \n python main.py -[r/g/l] [labels_file] video_name"
        raise Exception(INCORRECT_FORMAT_ERROR)
        
    elif sys.argv[1] == "-r":
        
        if len(sys.argv) != 3:
            print "Format is \n python main.py -[r/g/l] [labels_file] video_name"
            raise Exception(INCORRECT_FORMAT_ERROR)
            
        file_type = mimetypes.guess_type(sys.argv[2])[0]
        if file_type[:3] != "vid":#The file is not a video file
            print "Invalid video file"
            raise Exception(INCORRECT_VIDEO_FILE_ERROR)
            
        print "Recognizing: ", sys.argv[2]
        recog = Recognize(sys.argv[2])
        recog.recognize()

    elif sys.argv[1] == "-g":
        
        if len(sys.argv) != 4:
            print "Format is \n python main.py -[r/g/l] [labels_file] video_name"
            raise Exception(INCORRECT_FORMAT_ERROR)
        
        label_file_type = mimetypes.guess_type(sys.argv[2])[0]
        video_file_type = mimetypes.guess_type(sys.argv[3])[0]
        
        if label_file_type[:3] != "tex":#The file is not a labels file
            print "Invalid labels file"
            raise Exception(INCORRECT_LABEL_FILE_ERROR)
        
        if video_file_type[:3] != "vid":#The file is not a video file
            print "Invalid video file"
            raise Exception(INCORRECT_VIDEO_FILE_ERROR)
            
        print "Generating db for video: ", sys.argv[3], "\nwith labels file:", sys.argv[2]
        gen = Generate(sys.argv[2], sys.argv[3])
        gen.run()

    elif sys.argv[1] == "-l":
        
        if len(sys.argv) != 4:
            print "Format is \n python main.py -[r/g/l] [labels_file] video_name"
            raise Exception(INCORRECT_FORMAT_ERROR)
        
        label_file_type = mimetypes.guess_type(sys.argv[2])[0]
        video_file_type = mimetypes.guess_type(sys.argv[3])[0]
        
        if label_file_type[:3] != "tex":#The file is not a labels file
            return INCORRECT_LABEL_FILE_ERROR
        
        if video_file_type[:3] != "vid":#The file is not a video file
            return INCORRECT_VIDEO_FILE_ERROR
            
        print "Learning for video: ", sys.argv[3]
        video_name = sys.argv[3]
        ffmpeg.convert_video(video_name)
        name, extension = video_name[-5:].split('.')
        name = video_name.split('/')[-1]
        name = name[:-len(extension)-1]
        
        os.system("cp " + sys.argv[2] + " " + WEB_LABELS)        
        os.system("mv " + name + '.webm ' + 'web/output/static/output/' + WEB_VIDEO_NAME)
        print "Please go to the URL to edit labels"
        
    return SUCCESS

main()
