# CommercialDetection
GSOC 2015 project for Red Hen Labs. More details here http://vasanthkalingeri.github.io/CommercialDetection/

##Instructions to run
*Run dependencies.sh script
*Create a database in Mysql to store fingerprints
*Open src/constants.py, edit the line
  CONFIG = {
    "database": {
        "host": "127.0.0.1",
        "user": <username>,
        "passwd": <password>,
        "db": <name of the database created>
    }
  }
  
###To teach new commercials
*Create a file like data/labels for the given video
  python src/main.py -generate data/video.mpg data/labels.mpg
*The above creates a directory called db containing the commercials labelled. The system also learns from these commercials

###To detect commercials
  python src/main.py -recognize data/test.mpg
*This will create a file called output.txt containing the detected commercials.
*It will have unclassified sections which can later be seen and edited. The edited file can be used as labels file for learning new commercials.
*Edit content in output.txt after watching the video manually.
*Now using output.txt as labels for test.mpg, run the program again to update the db with new commercials.
  python src/main.py -generate data/test.mpg output.txt

##Results
The program was tested on Ubuntu 14.04 64 bit LTS. With the following versions of libraries
*Opencv cv = 2.4.8 
*Numpy = 1.8.2
*Scipy = 0.13.3
*ffmpeg = 2.6.2
