import subprocess
import requests
import sys

try:
    import youtube_dl
except ImportError:
    subprocess.call([sys.executable, "-m", 'pip', 'install', 'youtube-dl'])
    import youtube_dl

try:
    import inquirer
except ImportError:
    subprocess.call([sys.executable, "-m", 'pip', 'install', 'inquirer'])
    import inquirer

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.call([sys.executable, "-m", 'pip', 'install', 'beautifulsoup4'])

name_argument = str(sys.argv[1])

song_name = name_argument
song_name = song_name.split()
song_name = '+'.join(song_name)

request_url = "https://www.youtube.com/results?search_query={}".format(song_name)

markup = requests.get(request_url).text

soup = BeautifulSoup(markup, 'html.parser')
item_section = soup.select("ol.item-section > li")

s_href = ''
views = 0

checked = 0
class_exclusion_list = [
    "div.yt-lockup-playlist",
    "div.spell-correction",
    "div.yt-lockup-channel",
    "div.yt-lockup-movie-vertical-poster",
    "span.yt-badge.yt-badge-live"
]

song_dict = {}

exclude_current_class = False
for video in item_section:
    if checked > 3:
        break

    for class_ in class_exclusion_list:
        if len(video.select(class_)) > 0:
            exclude_current_class = True
            break

    if exclude_current_class:
        exclude_current_class = False
        continue

    title = video.select("h3.yt-lockup-title")[0].a['title']
    href = video.select("h3.yt-lockup-title")[0].a['href']

    view_count = video.select("div.yt-lockup-meta > ul.yt-lockup-meta-info > li")
    if len(view_count) > 1:
        view_count = view_count[1].string
    else:
        view_count = view_count[0].string
    title = title + '|' + view_count
    
    # print(view_count)
    song_dict[title] = href
    checked = checked + 1

songs_list = [
    inquirer.List('song_name',
            message="Which one?",
            choices=list(song_dict.keys())
        )
]

answer = inquirer.prompt(songs_list)
s_href = "https://www.youtube.com{}".format(song_dict[answer['song_name']])

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }]
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([s_href])
