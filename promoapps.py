import telebot
import time
import urllib
import requests
import sys
import feedparser
from telebot import types
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os

DESTINATION = os.environ['DESTINATION']
TOKEN = os.environ['BOT_TOKEN']
FEED_URL = os.environ['FEED_URL']

bot = telebot.TeleBot(TOKEN)
lastUpdates = 'history'
user_agent = {'User-agent': 'Mozilla/5.1'}

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
