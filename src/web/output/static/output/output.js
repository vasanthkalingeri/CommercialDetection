function play(time)
{
	var myPlayer = videojs('mainvid');
	videojs("mainvid").ready(function(){
          var myPlayer = this;
          // EXAMPLE: Start playing the video.
          myPlayer.currentTime(time);
    });
}
