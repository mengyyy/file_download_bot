# file_download_bot
a telegram bot download and send file 

## [Prepare](https://github.com/mengyyy/file_download_bot/blob/master/init.bash)

apt install python3 p7zip-full    
wget [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)    
python3 get-pip.py    
pip3 install requests bs4 python-telegram-bot    

## Config

edit [vk-config.json](https://github.com/mengyyy/file_download_bot/blob/master/vk-config.json)    
"chat_id" is an int which is a debug telegram chat id    
"my_token" is a string which is your telegram bot token    


## [Update](https://github.com/mengyyy/file_download_bot/blob/master/update_restart.sh)

wget -O vk_bot.py [https://raw.githubusercontent.com/mengyyy/file_download_bot/master/vk_bot.py](https://raw.githubusercontent.com/mengyyy/file_download_bot/master/vk_bot.py)    
ps ax | grep vk_bot.py | grep -v grep | cut -c 1-6 | xargs kill -9    
nohup python3 vk_bot.py &>/dev/null &    
