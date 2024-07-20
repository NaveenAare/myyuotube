
from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "https://www.youtube.com/watch?v=777hpBZDCkQ"
 
yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
print(yt.title)
 
ys = yt.streams.get_highest_resolution()
ys.download()