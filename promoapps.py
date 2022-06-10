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

def send_message(app_name, app_link, app_price, app_desc, app_img, btn_link):
    message = ('<b> ' + str(app_name) + '</b><a href="' + str(app_img) + '">.</a>'
        + '\n' + str(app_desc.replace("'",'')) 
        + '\n\n' + str(app_price))
    bot.send_message(f'@{DESTINATION}', message, parse_mode='HTML', reply_markup=btn_link)

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

def read_topic(link):
    response = requests.get(link, headers = user_agent)
    html = BeautifulSoup(response.content, 'html.parser')
    topic_title = html.title.text.strip()
    topic_split = topic_title.replace('[', ']')
    topic_split = topic_split.split(']')
    for index in range(len(topic_split)):
        if '$' in topic_split[index]:
            app_price = topic_split[index]
            if 'code' in app_price.lower():
                return False
            if 'free' in app_price.lower():
                app_price = app_price.lower().replace('free', '#Free')
    if '$' not in topic_title:
        return False
    links = html.findAll('a')
    for index in reversed(range(len(links))):
        links_index = links[index]
        links_get = links_index.get('href')
        if '://apps.apple.com/' in str(links_get) and checkUpdates(str(links_get), get_site()):
            app_link = links_get
            app_link = app_link.replace('/us/','/')
            response = requests.get(links_get)
            html = BeautifulSoup(response.content, 'html.parser')
            app_name = html.find('meta', {'property': 'og:title'})['content']
            app_name = app_name.split('on the App')[0]
            try:
                app_desc = html.find('div', {'class': 'section__description'}).text.strip()[:200]
            except AttributeError:
                app_desc = ''
            app_desc = app_desc.replace('Description\n','')
            try:
                app_img = html.find('meta', {'property': 'og:image:secure_url'})['content']
            except TypeError:
                continue
            print('Name: ' + str(app_name))
            print('Link: ' + str(app_link))
            #print('Yourls: ' + str(app_link))
            #print('Price: ' + str(app_price))
            #print('Desc: ' + str(app_desc[:200]) + '...')
            #print('OS: ' + str(app_os))
            #print('Img: ' + str(app_img))
            print('-'*80)
            btn_link = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('AppStore', url=app_link)
            btn_link.row(btn)
            send_message(app_name, app_link, app_price, app_desc, app_img, btn_link)

if __name__ == "__main__":
    feed = feedparser.parse(FEED_URL)
    htmltg = get_site()
    if not htmltg:
        exit()
    for item in feed['items'][:5]:
        link = item['link']
        read_topic(link)