from bs4 import BeautifulSoup
import requests
import os


URL = 'https://rozgrywkapodcast.pl/rozgrywka-213-the-drag/'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(
    class_='attachment-post-thumbnail size-post-thumbnail wp-post-image')

os.system(f"wget -P ./thumbnails {results['src']}")
# print(response.text)

# with open("test", 'wb') as f:
#     f.write(data)
