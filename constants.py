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

#For main.py
FREQ = 44100
WINDOW_SIZE = 1024
OVERLAP_RATIO = 0.1
STORE = "audio.csv"
OUTPUT = "output.txt"
SPEC_FOLDER = "specimages/"
SAVE_IMAGES = False
AUDIO_FILE = "aud.wav"
TEMP_FILE = "temp.png"
TIME_THRESH = 20

#For detect.py
SPEC_FOLDER = "specimages/"
THRESHOLD = 300

#For generate.py
DB_FOLDER = "db/"
DB_AUDIO = DB_FOLDER + "audio/"
DB_VIDEO = DB_FOLDER + "video/"
DBNAME = "commercials.csv"
DB_VERIFIED = "yes"
DB_GUESS = "no"

#For recognize.py
#in seconds
VIDEO_SPAN = 5 #How much to take to analyze audio
VIDEO_GAP = 10 #How much to skip
TEMP_VIDEO = "temp.mpg"
TEMP_AUDIO = "temp.wav"
