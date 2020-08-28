import os 
import glob
import random
import twitter
from podcastcutter import get_file_name

PATH = os.getenv("CUT_PATH")

def read_description(description_path):
    with open(description_path) as f:
        description = f.read()
    return description

def get_random_cut():
    cut_list = glob.glob(PATH + "*.mp4")
    cut_name = get_file_name(random.choice(cut_list))
    cut_mp4 = PATH + cut_name + ".mp4"
    cut_description = PATH + cut_name + ".txt"
    return cut_mp4, cut_description

def post_video(filepath, descritpion):
    api = twitter.Api(consumer_key=os.environ['CONSUMER_KEY'],
                      consumer_secret=os.environ['CONSUMER_SECRET'],
                      access_token_key=os.environ['ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
    status = api.PostUpdate(description, media=filepath)
    print("Posted to Twitter!")

if __name__ == "__main__":
    mp4_file, description_file = get_random_cut()
    print(mp4_file, description_file)
    post_video(mp4_file, description_file)
    os.system(f"rm {mp4_file} {description_file}")