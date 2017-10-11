#! /bin/bash

wget -O vk_bot.py https://raw.githubusercontent.com/mengyyy/file_download_bot/master/vk_bot.py
ps ax | grep vk_bot.py | grep -v grep | cut -c 1-6 | xargs kill -9
nohup python3 vk_bot.py &>/dev/null &
