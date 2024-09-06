import telebot
import time
import urllib
import requests
import sys
import feedparser
from telebot import types
from bs4 import BeautifulSoup
from atproto import Client, client_utils
import shutil
import xml.etree.ElementTree as ET
import os

DESTINATION = os.environ['DESTINATION']
TOKEN = os.environ['BOT_TOKEN']
FEED_URL = os.environ['FEED_URL']

bot = telebot.TeleBot(TOKEN)
lastUpdates = 'history'
user_agent = {'User-agent': 'Mozilla/5.1'}

def get_post_photo(url):
    response = requests.get(
        url,
        headers = {'User-agent': 'Mozilla/5.1'},
        timeout=3,
        verify=False
    )
    html = BeautifulSoup(response.content, 'html.parser')
    photo = html.find('meta', {'property': 'og:image'})['content']
    return photo

def bluesky_post(link, title):
    title = title.replace('[', '\n')
    title = title.replace(']', '')
    client = Client(base_url='https://bsky.social')
    client.login('promoapps.grf.xyz', os.environ.get('BLUESKY_PASSWORD'))
    text_builder = client_utils.TextBuilder()
    text_builder.link(
        title,
        link
    )
    
    photo = get_post_photo(link)
    file_name = photo.split("/")[-1]
    with requests.get(photo, stream=True) as r:
        with open(photo.split("/")[-1], 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    with open(file_name, 'rb') as f:
        image_data = f.read()
    client.send_image(
        text=text_builder,
        image=image_data,
        image_alt=title,
    )
    os.remove(file_name)

def send_message(url, title):
    title = title.replace('[', '\n')
    title = title.replace(']', '')
    message = (f'<b>{title}</b>\n{url}')
    try:
        bot.send_message(f'@{DESTINATION}', message, parse_mode='HTML')
    except:
        pass

def get_site():
    response = requests.get(f'https://t.me/s/{DESTINATION}')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def checkUpdates(param, html):
    return True
    link = param.split('/')[-1]
    if link not in str(html):
        return True
    return False

if __name__ == "__main__":
    feed = feedparser.parse(FEED_URL)
    htmltg = get_site()
    if not htmltg:
        exit()
    for item in feed['items'][:5]:
        for url in item['summary'].split('"'):
            if '://apps.apple.com/' in url:
                link = url
                title = item['title']
        try:
            print(link)
        except:
            continue
        if checkUpdates((link), get_site()):
            send_message(link, title)
            bluesky_post(link, title)
