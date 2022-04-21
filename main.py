import configparser
from logging import info , basicConfig , INFO
from telebot import TeleBot
import asyncio
import json


# config setup
config = configparser.ConfigParser()
config.read('config.ini')


# logging config 
basicConfig(level= INFO,
            format= '%(asctime)s %(levelname)s %(message)s',
            datefmt= '%Y-%m-%d %H:%M')


# telebot setup
botToken = config['telegram']['token']
bot =  TeleBot(botToken,  parse_mode="Markdown")


# upload file 
@bot.message_handler(commands=['upload'])
def upload(message):
    bot.register_next_step_handler(bot.reply_to(message , 'Pls upload your json file'), upload_file)

def upload_file(message):
    if message.document.file_name[-5:] != ".json":
        bot.reply_to(message , "Wrong file type")
        return ''

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('result.json' , 'wb') as file:
        file.write(downloaded_file)
    
    bot.reply_to(message , "Data updated ! You can check yout chat history by using cmd on that group")


# word count 
@bot.message_handler(commands="word")
def number(message):
    f = open('result.json','r',encoding="utf-8")
    search = message.text.replace("/word ", "")
    data = json.load(f)

    list = []
    name = []
    count = 0 
    for msg in data["messages"]:
        if msg["type"] != "message":
            continue

        if search in msg["text"]:
            count += 1 
            if msg["from"] in name:
                list[name.index(msg["from"])] += 1 
            else:
                name.append(msg["from"])
                list.append(1)

    bot.reply_to(message , "word {} mentioned {} times ".format(search, count))

    msg = ""
    
    for i in range(len(list)):
        msg += str(name[i]) + " : _" + str(list[i]) + "_ " + "\n"

    bot.reply_to(message , msg) 


# run telebot
asyncio.run(bot.infinity_polling())
