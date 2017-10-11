#! /usr/bin/python3
# -*- coding:utf-8 -*-

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import RegexHandler
from telegram.ext import BaseFilter
import pprint
import re
import bs4
import requests
import os
import logging
import subprocess
import time
import json

log_file_enable = True
logger = logging.getLogger('tcp_test')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')

if log_file_enable:
    log_time_str = time.strftime('%Y_%m_%d_%H_%M', time.localtime())
    log_path = '/home/Downloads/vk_bot_{}.log'.format(log_time_str)
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

with open('vk-config.json') as data_file:
    data = json.load(data_file)

chat_id = data['chat_id']
my_token = data['my_token']

vk_url_re = re.compile('https://vk\.com/doc\d*_\d*')

bot = telegram.Bot(my_token)
bot.send_message(chat_id=chat_id, text="Hello World")
updates = bot.get_updates()

cmd_7z = "7z a -v49m -y '{}' '{}' -mx0"
os.chdir('/home/Downloads')


def file_split_7z(file, split_size=50):
    fz = os.path.getsize(file) / 1024 / 1024
    pa = round(fz / split_size)
    fn = os.path.splitext(file)[0]
    subprocess.call(cmd_7z.format(fn, file), shell=True)
    file_list = []
    for i in range(pa):
        file_list.append('{}.7z.{:03d}'.format(fn, i + 1))
    return file_list


def get_url_frrm_message(message):
    url_list = []
    for entity in message.entities:
        offset = entity.offset
        length = entity.length
        url_list.append(message.text[offset: offset + length])
    return url_list


class VK_Filter(BaseFilter):

    def filter(self, message):
        logger.info('check vk link {}'.format(message.text))
        if vk_url_re.search(message.text):
            return True


vk_filter = VK_Filter()


def deal_vk_file_url(vk_url):
    try:
        req = requests.get(vk_url)
        if req.headers['Content-Type'].startswith('text/html'):
            bso = bs4.BeautifulSoup(req.content, 'html.parser')
            file_name = bso.title.text
            surl = bso.find('iframe').attrs['src']
            req = requests.get(surl)
        else:
            hl = req.history[-1].headers['Location']
            hlo = requests.compat.urlparse(hl)
            file_name = hlo.path.split('/')[-1]
        with open(file_name, 'wb') as f:
            f.write(req.content)
        if len(req.content) > 49 * 1024 * 1024:
            file_name_list = file_split_7z(file_name)
        else:
            file_name_list = [file_name]
    except Exception as e:
        logger.exception('message')
    else:
        logger.info('{} downloaded'.format(file_name_list))
        return file_name_list


def deal_vk_link(bot, update):
    vk_url_list = get_url_frrm_message(update.message)
    gg = [deal_vk_file_url(i) for i in vk_url_list]
    logger.info('gg is\n')
    logger.info(pprint.pformat(gg))
    for file_list in gg:
        for file in file_list:
            try:
                bot.send_chat_action(chat_id=update.message.chat_id,
                                     action=telegram.ChatAction.UPLOAD_DOCUMENT)
                cc = update.message.reply_document(document=open(file, 'rb'),
                                                   timeout=60)
                update.message.reply_text(cc.document.file_id)
            except Exception as e:
                logger.exception('message')
            finally:
                os.remove(file)


def get_file_by_id(bot, update, args):
    logger.debug('args is {}'.format(args))
    if len(args) == 0:
        update.message.reply_text(
            'usage:\n/file BQADBQADBwADjBfoVthU7XOsRwP2Ag')
    for i in args:
        try:
            update.message.reply_document(document=i,
                                          timeout=60)
        except Exception as e:
            logger.exception('message')
            update.message.reply_text('file id error')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


if __name__ == '__main__':
    # updater = Updater(token=my_token, request_kwargs=request_kwargs)
    updater = Updater(token=my_token)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(vk_filter, deal_vk_link))
    dp.add_handler(CommandHandler('file', get_file_by_id,
                                  pass_args=True,))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
