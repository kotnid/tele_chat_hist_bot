import configparser
from logging import info , basicConfig , INFO
from telebot import TeleBot
import asyncio
import json
from time import sleep
from os import path , remove
import pandas
import matplotlib.pyplot as plt


plt.switch_backend('agg')


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


# message count
@bot.message_handler(commands="msg_count")
def msg_count(message):
    #f = open('ChatExport_2022-03-14 (1)\\result.json','r',encoding="utf-8")
    f = open('result.json','r',encoding="utf-8")
    data = json.load(f)

    name = []
    for msg in data["messages"]:
        if msg["type"] != "message":
            continue
        try:
            if msg["from"] not in name:
                name.append(msg["from"]) 
        except:
            pass

    
    for people in name:
        df = pandas.DataFrame(data["messages"])
        df = df.rename(columns={"from":"name"})
        df = df.query("type == 'message'").query(f"name == '{people}'")
        df = df[['date']]
        df['date'] = pandas.to_datetime(df['date'])
        df['count'] = 1
        df = df.resample("W", on='date').agg({'count':'sum'}).reset_index()
        df['sum'] = df['count'].cumsum()
        plt.plot(df["date"] , df["sum"]  , label=people)

    plt.legend()
    plt.title('Total msg')
    plt.xlabel('time')
    plt.ylabel('amount')
    plt.gcf().autofmt_xdate()
    plt.savefig('plot.jpg')
    plt.clf()
    bot.send_photo(message.chat.id , photo=open("plot.jpg" , "rb"))

    sleep(3)
    if path.exists("plot.jpg"):
        remove("plot.jpg")


# sticker count
@bot.message_handler(commands="sticker_count")
def sticker_count(message):
    f = open('result.json','r',encoding="utf-8")
    data = json.load(f)

    name = []
    for msg in data["messages"]:
        if msg["type"] != "message":
            continue
        try:
            if msg["media_type"] == "sticker":
                if msg["from"] not in name:
                    name.append(msg["from"]) 
        except:
            pass

    
    for people in name:
        df = pandas.DataFrame(data["messages"])
        df = df.rename(columns={"from":"name"})
        df = df.query("type == 'message'").query(f"media_type == 'sticker'").query(f"name == '{people}'")
        df = df[['date']]
        df['date'] = pandas.to_datetime(df['date'])
        df['count'] = 1
        df = df.resample("W", on='date').agg({'count':'sum'}).reset_index()
        df['sum'] = df['count'].cumsum()
        plt.plot(df["date"] , df["sum"]  , label=people)

    plt.legend()
    plt.title('Total used of the stickers')
    plt.xlabel('time')
    plt.ylabel('amount')
    plt.gcf().autofmt_xdate()
    plt.savefig('plot.jpg')
    plt.clf()
    bot.send_photo(message.chat.id , photo=open("plot.jpg" , "rb"))

    sleep(3)
    if path.exists("plot.jpg"):
        remove("plot.jpg")


# run telebot
asyncio.run(bot.infinity_polling())
