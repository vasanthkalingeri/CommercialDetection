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


#For detect.py
SPEC_FOLDER = "specimages/"
THRESHOLD = 300

#For generate.py
DB_FOLDER = "../db/"
DB_AUDIO = DB_FOLDER + "audio/"
DB_VIDEO = DB_FOLDER + "video/"
DBNAME = "../commercials.csv"
DB_CLASSIFIED = "yes"#"classified"
DB_UNCLASSIFIED = "no"#"Not classified"

#For audiodetect
WINDOW_SIZE = 0.03 #In seconds
OVERLAP = 0#0-1 ratio

#For recognize.py
OUTPUT = "output.txt"
SILENCE = "silence"

#in seconds
VIDEO_SPAN = 5 #How much to take to analyze audio
VIDEO_GAP = 10 #How much to skip
TEMP_VIDEO = "../data/temp.mpg"
TEMP_AUDIO = "../data/temp.wav"

#For shotdetect.py
HIST_CHANGE_THRESH = 0.98

#For fileHandler
TEMP_FILE = 'temp'
TV_SHOW = "TV"
COMMERCIAL = "commercial"
UNCLASSIFIED_CONTENT = "unclassified"
