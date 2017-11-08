import os
from database import get_database, Database
import dejavu_fingerprint as djv_fingerprint
import numpy as np
import multiprocessing
import traceback
import sys
import pydub
from timeFunc import get_seconds, get_time_string
from hashlib import sha1

class ComDet(object):

    AD_ID = "ad_id"
    AD_NAME = 'ad_name'
    AD_DURATION = 'duration'
    CONFIDENCE = 'confidence'
    MATCH_TIME = 'match_time'
    OFFSET = 'offset'
    OFFSET_SECS = 'offset_seconds'

    def __init__(self, config={}):

        config.setdefault('database', {
                                    "host": "127.0.0.1",
                                    "user": "root",
                                    "passwd": "pass",
                                    "db": "dejavu"
                                    })
        config.setdefault('database_type', 'mysql')
        config.setdefault('analyze_span', 5)
        config.setdefault('analyze_skip', 15)
        config.setdefault('confidence_thresh', 100)

        self.config = config
        # initialize db
        db_cls = get_database(config.get("database_type", 'None'))

        self.db = db_cls(**config.get("database", {}))
        self.db.setup()

    def get_fingerprinted_ads(self):
        # get ads previously indexed
        self.ads = self.db.get_ads()
        self.adhashes_set = set()  # to know which ones we've computed before
        for ad in self.ads:
            ad_hash = ad[Database.FIELD_FILE_SHA1]
            self.adhashes_set.add(ad_hash)

    def _get_nprocess(self):
        # Try to use the maximum amount of processes if not given.
        try:
            nprocesses = nprocesses or multiprocessing.cpu_count()
        except NotImplementedError:
            nprocesses = 1

        nprocesses = 1 if nprocesses <= 0 else nprocesses
        return nprocesses

    def fingerprint_file(self, input_file_path, input_labels, nprocesses=None):

        """
            Function: (Part of code majorly borrows from Dejavu)
                Creates fingerprints for input_file with names from labels_file

                Given any input_file_path uses pydub to just read the file
                Supports all formats supported by ffmpeg

            Set a parallel pool of workers where each worker creates a fingerprint for the ad
            specified in the labels file.

            The entire ad is stored in the database as SHA hash which is used to check for duplicate
            entries of the same ad by content.
            Duplicate ads are ignored. Duplicate here refers to content and not the name of the ad

            Inputs:
                input_file_path: Either video or audio file
                input_labels: 2D list of ads where each element of list is
                        [start_time, end_time, ad_name] for that ad.
                        start_time, end_time is in seconds from the start of the audio
        """
        pool = multiprocessing.Pool(nprocesses)

        ads_to_fingerprint = []
        audios_to_fingerprint = []

        ext = input_file_path.split('.')[-1]
        audio = pydub.AudioSegment.from_file(input_file_path, ext)
        audio = audio.set_channels(1)

        self.get_fingerprinted_ads()

        for strt,end,ad_name in input_labels:
            # don't refingerprint already fingerprinted ads
            chunk = audio[strt*1000:end*1000]
            ad_hash = _unique_hash(chunk).upper()
            if ad_hash in self.adhashes_set:
                print "%s already fingerprinted, continuing..." % ad_name
                continue

            ads_to_fingerprint.append(ad_name)
            audios_to_fingerprint.append(chunk)

        worker_input = zip(ads_to_fingerprint, audios_to_fingerprint)

        # Send off our tasks
        iterator = pool.imap_unordered(_fingerprint_worker,
                                       worker_input)

        # Loop till we have all of them
        while True:
            try:
                ad_name, hashes, ad_hash, duration = iterator.next()
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                break
            except:
                print("Failed fingerprinting")
                # Print traceback because we can't reraise it here
                traceback.print_exc(file=sys.stdout)
            else:
                aid = self.db.insert_ad(ad_name, ad_hash, duration)

                self.db.insert_hashes(aid, hashes)
                self.db.set_ad_fingerprinted(aid)
                self.get_fingerprinted_ads()

        pool.close()
        pool.join()

    def find_matches(self, samples, Fs=djv_fingerprint.DEFAULT_FS):

        hashes = djv_fingerprint.fingerprint(samples, Fs=Fs)
        return self.db.return_matches(hashes)

    def align_matches(self, matches):
        """
            Finds hash matches that align in time with other matches and finds
            consensus about which hashes are "true" signal from the audio.

            Returns a dictionary with match information.
        """
        # align by diffs
        diff_counter = {}
        largest = 0
        largest_count = 0
        ad_id = -1
        for tup in matches:
            aid, diff = tup
            if diff not in diff_counter:
                diff_counter[diff] = {}
            if aid not in diff_counter[diff]:
                diff_counter[diff][aid] = 0
            diff_counter[diff][aid] += 1

            if diff_counter[diff][aid] > largest_count:
                largest = diff
                largest_count = diff_counter[diff][aid]
                ad_id = aid

        # extract idenfication
        ad = self.db.get_ad_by_id(ad_id)

        # return match info
        nseconds = round(float(largest) / djv_fingerprint.DEFAULT_FS *
                         djv_fingerprint.DEFAULT_WINDOW_SIZE *
                         djv_fingerprint.DEFAULT_OVERLAP_RATIO, 5)

        #Will only return valid ads that were detected from the database.
        if ad and int(largest_count) >= self.config['confidence_thresh'] and (0 <= nseconds <= ad[Database.FIELD_DURATION]):
            # TODO: Clarify what `get_ad_by_id` should return.
            adname = ad.get(ComDet.AD_NAME, None)
            duration = ad[ComDet.AD_DURATION]
        else:
            return None

        ad = {
            ComDet.AD_ID : ad_id,
            ComDet.AD_NAME : adname,
            ComDet.AD_DURATION: duration,
            ComDet.CONFIDENCE : largest_count,
            ComDet.OFFSET : int(largest),
            ComDet.OFFSET_SECS : nseconds}
        return ad

    def recognize_segment(self, audio_segment):
        """
            Function:
                Given an audio segment recognize the ad present in it.

            Input:
                audio_segment: Pydub's audio segment

            Returns:
                [name, confidence, offset, duration]
        """
        data = np.fromstring(audio_segment._data, np.int16)
        data = data[0::audio_segment.channels]
        Fs = audio_segment.frame_rate
        matches = self.find_matches(data, Fs=Fs)
        return self.align_matches(matches)

    def recognize_ads_file(self, input_file_path):
        """
            Function:
                Recognize all the commercials present in the file

                1) Convert input_file to wav file
                2) Process the file in chunks
                3) Skip parts based on the offset and duration of recognize_chunk
                4) Append [start_time, end_time, name] of each confident segment
            
            Input:
                input_file_path: Either video or audio file whose ads have to be detected.

            Returns:
                List of [start_time, end_time, name] of all the ads detected in the file
        """
        ext = input_file_path.split('.')[-1]
        audio = pydub.AudioSegment.from_file(input_file_path, ext)
        audio = audio.set_channels(1)

        strt = 0
        duration = audio.duration_seconds

        labels = []
        while strt < duration - self.config['analyze_span']:
            end = strt + self.config['analyze_span']
            audio_segment = audio[strt*1000:end*1000]    
            ad = self.recognize_segment(audio_segment)

            if ad:
                strt = int(strt - ad[ComDet.OFFSET_SECS])
                end = int(strt + ad[ComDet.AD_DURATION])
                strt_string = get_time_string(strt)
                end_string = get_time_string(end)
                print "Found:", strt_string, end_string, ad[ComDet.AD_NAME], ad[ComDet.CONFIDENCE]
                labels.append([strt_string, end_string, ad[ComDet.AD_NAME]])
                strt = end
            else:
                strt += self.config['analyze_skip']
        return labels

    def clear_data(self):
        """
            Clear the database of all contents
        """
        
        self.db.empty()

def _unique_hash(audio):

    #Create a hash of the entire audio
    data = np.fromstring(audio._data, np.int16)
    return sha1(data).hexdigest()

def _fingerprint_worker(input):

    # Pool.imap sends arguments as tuples so we have to unpack
    # them ourself.
    try:
        ad_name, audio = input
    except:
        pass

    data = np.fromstring(audio._data, np.int16)
    channel = data[0::audio.channels]
    Fs = audio.frame_rate

    result = set()

    print("Fingerprinting %s" % (ad_name))
    hashes = djv_fingerprint.fingerprint(channel, Fs=Fs)
    print("Finished %s" % (ad_name))
    result |= set(hashes)
    ad_hash = _unique_hash(audio)
    duration = audio.duration_seconds
    return ad_name, result, ad_hash, duration

def test_generate():

    input_file_path = '../test/test.mp4'
    labels_file_path = '../test/test_labels.txt'
    input_labels = []
    for line in open(labels_file_path):
        line = line.strip()
        strt_string, end_string, ad_name = line.split(' - ')
        strt = get_seconds(strt_string)
        end = get_seconds(end_string)
        input_labels.append([strt, end, ad_name])

    ad_det = ComDet()
    ad_det.fingerprint_file(input_file_path, input_labels)

def test_recognize():

    input_file_path = '../test/test.mp4'
    ad_det = ComDet()
    ad_det.recognize_ads_file(input_file_path)

if __name__ == '__main__':
    test_generate()
    test_recognize()