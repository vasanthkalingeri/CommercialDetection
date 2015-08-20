#For dejavu
CONFIG = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "pass",
        "db": "dejavu"
    }
}
DJV_CONFIDENCE = "confidence"
DJV_SONG_NAME = "song_name"
DJV_OFFSET = "offset_seconds"
CONFIDENCE_THRESH = 10

#For generate.py
DB_FOLDER = "../db/"
DB_AUDIO = DB_FOLDER + "audio/"
DB_VIDEO = DB_FOLDER + "video/"
DBNAME = "../commercials.csv"
VIDEO_EXT = ".mpg"
AUDIO_EXT = ".wav"

#For recognize.py
OUTPUT = "output.txt"

#in seconds
VIDEO_SPAN = 5 #How much to take to analyze audio
VIDEO_GAP = 15 #How much to skip
TEMP_VIDEO = "../data/temp.mpg"
TEMP_AUDIO = "../data/temp.wav"

#For fileHandler
UNCLASSIFIED_CONTENT = "unclassified"

#For web content
WEB_VIDEO_NAME = 'out2.webm'
WEB_LABELS = 'labels.txt'
