import timeFunc
from constants import *
import os

class LabelsFile(object):
    
    def __init__(self, infile=None, outfile=None):
        
        self.filename = infile
        self.newfile = outfile
        self.write_count = 0
        
    def read_lables(self, skip=True):
        
        """"Returns: [start, end, name]
            skip = True means skips all the labels which do not start with ad"""
        
        with open(self.filename) as fd:
            for line in fd:
                line = line.split("=")
                if len(line) == 1: #In case of blank lines
                    break
                line = [i.strip() for i in line]
                time = line[0].split("-")
                time = [i.strip(" ") for i in time]
                name = line[-1].strip()
                if (skip is True) and (name[:2] != 'ad'): #Get only ad contents
                    continue
                yield [time[0], time[1], name]
    
    def write_labels(self, content):
        
        """
            Content is in form of a list [start, end, name] 
            Where start and end can be given in seconds or as a string
        """
        
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
    
    def __init__(self, filename):
    
        self.filename = filename
    
    def get_line(self, index):
        
        f = open(self.filename)
        i = 0
        for line in f:
            if i == index:
                line = line.split(",")
                name = line[0]
                duration = line[1]
                verified = line[-1]
                duration = timeFunc.get_seconds(duration)
                return [name, duration, verified]
            i += 1
        print index, i
        raise Exception("Csv file and mysqldb are not in sync.")
        return -1
    
#def test():
#    
#    LabelsFile('output.txt').generate_tv(4)
##    LabelsFile('output.txt').write_labels('test', [1, 1, 'name'])

#test()
