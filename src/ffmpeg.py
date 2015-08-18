import os

def create_video(start, duration, video_src, video_dst, force_fps=False, fps=60):
    
    print
    print "Creating the video",video_dst
    os.system("ffmpeg -ss " + start + " -i " + video_src + " -t " + duration + " -acodec copy -vcodec copy " + video_dst + " -loglevel quiet")
    if force_fps:
        os.system("ffmpeg -ss " + video_dst + " -vf fps=1/" + str(fps) + " " + video_dst)
    print "Video created!!"
    print
    
def create_audio(video_src, audio_dst, rate=44100, channels=1, block="160k"):
    
    print
    print "Creating audio for the video"
    os.system("ffmpeg -i " + video_src + " -ab " + block + " -ac " + str(channels) + " -ar " + str(rate) + " -vn " + audio_dst + " -loglevel quiet")
    print "Audio created!!"
    print
    
def create_images(video_name, fps, folder):

    os.system("ffmpeg -i " + video_name + " -vf fps=1/" + str(fps) + " " + folder + "%d.png")
    
def convert_video(video_name, cpu_cores=4, preset="superfast"):
    
    print "Converting video so that it can be played on browser..."
    name, extension = video_name[-5:].split('.')
    name = video_name.split('/')[-1]
    name = name[:-len(extension)-1]
    
    print name, extension
    os.system("ffmpeg -i " + video_name + " -r 5 -cpu-used " + str(cpu_cores) +" " + name + ".webm -preset " + preset)
    print "Conversion done!!"
