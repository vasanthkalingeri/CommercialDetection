from dejavu import Dejavu
from dejavu.recognize import FileRecognizer

config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "pass",
        "db": "dejavu"
    }
}

djv = Dejavu(config)

def test():

#    djv.fingerprint_directory("db/audio", [".wav"])
    print djv.db.get_num_fingerprints()
    song = djv.recognize(FileRecognizer, "db/audio/1.wav")
    print song
    
test()
