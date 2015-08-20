ffmpeg -i data.mpg -ss 00:08:00 -to 00:11:20 -c copy cut.mp4; #Cuts the data from data.mpg from 1:00 to 11:20 and writes it to cut.mp4

ffmpeg -i cut.mp4 -ab 160k -ac 1 -ar 44100 -vn audio.wav; #Extracts the audio from the video

ffmpeg -i input.jpg -vf scale=320:-1 output_320.png

#https://trac.ffmpeg.org/wiki/Create%20a%20thumbnail%20image%20every%20X%20seconds%20of%20the%20video

ffmpeg -i out50.mpg -vf select="eq(pict_type\,PICT_TYPE_I)" -vsync 0 data/%d.png -loglevel debug 2>&1 | grep select:1 > keyframes.txt #used to display i frames

ffprobe -select_streams v -show_frames out50.mpg; #used to select frame info

ffmpeg -i video.mpg -vf scale=100:100 -acodec copy out.mpg

scp -P 5022 vasanth@gsocdev.ccextractor.org:/data/2015-04-28_0635_US_KABC_Jimmy_Kimmel_Live.mpg .
