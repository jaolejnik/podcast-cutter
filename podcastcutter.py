import os
import time
import json
import random
import twitter
import feedparser
import urllib.request
import moviepy.editor as mpy
from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.playback import play


def init_json(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path) as f:
        return json.load(f)

SECONDS = 1000


def get_file_name_extension(file_path):
    name = file_path
    slash_index = file_path.rfind('/')
    if slash_index != -1:
        name = name[slash_index+1:]
    if '.' not in name:
        return [name, '']
    name_ext = name.split('.')
    if len(name_ext) == 1: name_ext.insert(0,'')
    return name_ext

def get_file_name(file_path):
    return get_file_name_extension(file_path)[0]

def get_file_extension(file_path):
    return get_file_name_extension(file_path)[1]

def format_ms(miliseconds):
    seconds = miliseconds // SECONDS
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def get_episode_file(rss_url):
    print("Getting RSS feed from:", rss_url)
    feed = feedparser.parse(rss_url)

    random_episode = random.choice(feed['entries'])
    title = random_episode['title']
    print("Chosen episode:", title)
    site_link = random_episode['links'][0]['href']
    audio_link = random_episode['links'][1]['href']
    name_index = audio_link.rfind('/') + 1
    file_name = audio_link[name_index:]

    print("Downloading episode:", title)
    os.system(f"wget {audio_link}")
    print("Download complete!")
    return file_name, title, site_link

def get_episode_cover(site_link):
    if site_link == "http://rozgrywkapodcast.pl/":
        return f"logo-nowe.png"
    page = urllib.request.urlopen(site_link).read()
    soup = BeautifulSoup(page, 'html.parser')
    results = soup.find(class_='attachment-post-thumbnail size-post-thumbnail wp-post-image')
    image_url = results['src']
    name_extension_tuple = get_file_name_extension(image_url)
    os.system(f"wget {image_url}")
    image_file_name = ".".join(name_extension_tuple)
    return image_file_name

def get_random_slice(file_path, slice_duration):
    loaded_episode = AudioSegment.from_mp3(file_path)
    print(f"Loaded {file_path} for slicing.")
    duration = len(loaded_episode)
    sample_duration = slice_duration * SECONDS
    random_ms = random.randrange(0, duration-sample_duration, SECONDS)
    sample = loaded_episode[random_ms:random_ms+sample_duration]
    sample = sample.fade_in(2*SECONDS)
    sample = sample.fade_out(2*SECONDS)
    new_file_path = 'cut_' + file_path
    sample.export(new_file_path, format='mp3')
    print("Saved sliced file to", new_file_path)
    return new_file_path, [random_ms, random_ms+sample_duration]

def create_video(image_path, audio_path):
    print(f"Loaded {image_path}, {audio_path} to create a video")
    silent_intro = mpy.ImageClip(image_path, duration=2)
    video = mpy.ImageClip(image_path, duration=10)
    audio = mpy.AudioFileClip(audio_path)
    clip = video.set_audio(audio)
    final_clip = mpy.concatenate_videoclips([silent_intro, clip])
    clip_name = get_file_name(audio_path) + '.mp4'
    final_clip.write_videofile(clip_name, fps=1, audio_codec='aac')
    print("Saved the video to ", clip_name)
    return clip_name

def cleanup(file_path='.'):
    print("Started cleanup.")
    files = os.listdir()
    for file in files:
        name = get_file_name(file)
        ext = get_file_extension(file)
        if name != 'logo-nowe':
            if ext.lower() in ['mp3', 'mp4', 'png', 'jpg', 'jpeg']:
                os.remove(file)
                print("Deleted ", file)

def create_description(timestamps, episode_url, episode_title):
    return f"{episode_title}\n{timestamps[0]} - {timestamps[1]}\nPrzesłuchaj cały odcinek tutaj:\n{episode_url}"

def post_video(filepath, timestamps, episode_url, episode_title):
    description = create_description(timestamps, episode_url, episode_title)

    api = twitter.Api(consumer_key=os.environ['CONSUMER_KEY'],
                      consumer_secret=os.environ['CONSUMER_SECRET'],
                      access_token_key=os.environ['ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
    print("Posted to Twitter!")
    status = api.PostUpdate(description, media=filepath)

def quality_control(audio_path):
    print("Quality control.")
    sample = AudioSegment.from_mp3(audio_path)
    play(sample)
    while True:
        test = input("Was it funny? (R - play again):\n")
        if test.upper() == 'Y' or len(test) == 0:
            print("Funny.")
            print("Resuming...")
            return True
        elif test.upper() == 'R':
            play(sample)
        else:
            print("Not funny.")
            cleanup()
            print("Starting over...")
            return False

if __name__ == "__main__":
    rozgrywka_rss = os.environ['RSS_URL']
    episode_path, episode_title, episode_url = get_episode_file(rozgrywka_rss)
    episode_cover = get_episode_cover(episode_url)
    slice_path, timestamps = get_random_slice(episode_path, 12)
    timestamps = list(map(format_ms, timestamps))
    video_path = create_video(episode_cover, slice_path)
    post_video(video_path, timestamps, episode_url, episode_title)
    cleanup()
