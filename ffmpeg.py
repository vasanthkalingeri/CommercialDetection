import os

def create_video(start, duration, video_src, video_dst):
    
#    print "ffmpeg -ss " + start + " -i " + video_src + " -t " + duration + " -acodec copy -vcodec copy " + video_dst
    os.system("ffmpeg -ss " + start + " -i " + video_src + " -t " + duration + " -acodec copy -vcodec copy " + video_dst)

def create_audio(video_src, audio_dst, rate="44100", channels="1", block="160k"):
    
#    print "ffmpeg -i " + video_src + " -ab " + block + " -ac " + channels + " -ar " + rate + " -vn " + audio_dst
    os.system("ffmpeg -i " + video_src + " -ab " + block + " -ac " + channels + " -ar " + rate + " -vn " + audio_dst)
