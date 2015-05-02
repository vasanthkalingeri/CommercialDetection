ffmpeg -i data.mpg -ss 00:01:00 -to 00:12:20 -c copy cut.mp4; #Cuts the data from data.mpg from 1:00 to 11:20 even though 12:20 is specified and writes the file cut.mp4

ffmpeg -i cut.mp4 audio.wav; #Extracts the audio from the video

