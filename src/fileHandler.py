"""
    This file deals with all operations involving files.
"""

import timeFunc
from constants import *
import os
import mimetypes

class LabelsFile(object):
    
    """
        Used to handle operations on the output file or the label file that is given as input
    """
    
    def __init__(self, infile=None, outfile=None):
        
        self.filename = infile
        self.newfile = outfile
        self.write_count = 0
        
        if self.filename:
            label_file_type = mimetypes.guess_type(self.filename)[0]
            if label_file_type[:3] != "tex":#The file is not a labels file
                print "Incorrect label file"
                raise Exception(INCORRECT_LABEL_FILE_ERROR)
        
        if self.newfile:
            label_file_type = mimetypes.guess_type(self.newfile)[0]
            if label_file_type[:3] != "tex":#The file is not a labels file
                print "Incorrect label file"
                raise Exception(INCORRECT_LABEL_FILE_ERROR)
        
    def read_lables(self, skip=True):
        
        """
            skip = True means skips all the labels which do not start with ad
            The labels file is of the format:
                start_time - end_time = name_of_content
            This reads the file and returns each of the values
            
            Returns: [start, end, name] All are string
        """
        
        with open(self.filename) as fd:
            for line in fd:
                line = line.split("=")
                if len(line) == 1: #In case of blank lines
                    break
                line = [i.strip() for i in line]
                time = line[0].split("-")
                time = [i.strip(" ") for i in time]
                name = line[-1].strip()
                if (skip is True) and (name[:2] != 'ad'):
                    #If does not start with ad, then we continue to the next line
                    continue
                    
                yield [time[0], time[1], name]
    
    def write_labels(self, content):
        
        """
            Content is in form of a list [start, end, name] 
            Where start and end can be given in seconds or as a string
        """
        
        #If we are writing for the first time, then we open the file in write mode so that previous contents are erased
        if self.write_count == 0:
            f = open(self.newfile, 'w')
        else:
            f = open(self.newfile, 'a')
        
        start = content[0]
        end = content[1]
        name = content[2]
        line = ""
        if type(start) == type(end) == int:
            line = timeFunc.get_time_string(start) + " - " + timeFunc.get_time_string(end) + " = " + name
        elif type(start) == type(end) == str:
            line = start + " - " + end + " = " + name
        line += '\n'
        f.write(line)
        f.close()
        self.write_count += 1

class DatabaseFile(object):
    
    """
        Used to handle operations on the database csv file
    """
    
    def __init__(self, filename):
    
        self.filename = filename
        
        #Checking if the type of file is right
        label_file_type = mimetypes.guess_type(self.filename)[0]
        if (label_file_type[:3] != "tex") and self.filename[-3:] != "csv":
            #The file is not a correct database file
            print "Incorrect database file"
            raise Exception(INCORRECT_DB_FILE_ERROR)
        
    def get_line(self, index):
        
        """
            Function gets the line in the database file based on the index.
            The index is acting as the line number in the database file.
            Returns: [name(string), duration(int)] 
        """
        
        f = open(self.filename)
        i = 0
        for line in f:
            if i == index:
                line = line.split(",")
                name = line[0]
                duration = line[1]
                duration = timeFunc.get_seconds(duration)
                return [name, duration]
            i += 1
        print index, i
        print "Db and csv are not in sync"
        raise Exception(DB_CSV_OUT_OF_SYNC_ERROR)
        return -1
    
#def test():
#    
#    LabelsFile(OUTPUT)
##    LabelsFile('output.txt').write_labels('test', [1, 1, 'name'])

#test()
