import configparser
from logging import info , basicConfig , INFO
from telebot import TeleBot
import asyncio
import json
from time import sleep
from os import path , remove
import pandas
import matplotlib.pyplot as plt
from zipfile import ZipFile
from shutil import rmtree
from pandas import DataFrame


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


# tutorial
@bot.message_handler(commands=['start','help'])
def start(message):
    bot.reply_to(message , '''
/help - show this msg
/start - show this msg
/upload - upload zip file
/word - word count
/msg_count - message count
/sticker_count - sticker count
/sticker - sticker ranking
/check - specific sticker count
''')


# upload file 
@bot.message_handler(commands=['upload'])
def upload(message):
    bot.register_next_step_handler(bot.reply_to(message , 'Pls upload your zip file'), upload_file)

def upload_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('result.zip' , 'wb') as file:
        file.write(downloaded_file)
    
    if path.exists('data'):
        rmtree('data')

    with ZipFile('result.zip', 'r') as zip_ref:
        zip_ref.extractall()
    
    remove('result.zip')
    bot.reply_to(message , "Data updated ! You can check yout chat history by using cmd on that group")


# word count 
@bot.message_handler(commands="word")
def number(message):
    bot.register_next_step_handler(bot.reply_to(message , 'Pls enter the word'), word_search)


def word_search(message):
    f = open('data/result.json','r',encoding="utf-8")
    search = message.text
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
    f = open('data/result.json','r',encoding="utf-8")
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
    f = open('data/result.json','r',encoding="utf-8")
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


# stickre ranking
@bot.message_handler(commands="sticker")
def sticker(message):
    bot.register_next_step_handler(bot.reply_to(message , 'Pls enter the start and end'), sticker_rank)

def sticker_rank(message):
    f = open('data\\result.json','r',encoding="utf-8")
    data = json.load(f)
    list = message.text.split(' ')
    search = list[0]
    end = list[1]
    list = []
    name = []
    count = 0 
    for msg in data["messages"]:
        if msg["type"] != "message":
            continue
        try:
            if msg["media_type"] == "sticker":
                count += 1

                if msg["file"] in name:
                    list[name.index(msg["file"])] += 1 

                else:
                    name.append(msg["file"])
                    list.append(1)
        except:
            pass


    df = DataFrame({'name' : name,
                'amount' : list})

    df = df.nlargest(int(search),'amount')

    file = df['name'].tolist()
    amount = df["amount"].tolist()

    bot.reply_to(message , f"Top {search} - {end} of sticker in the group")

    for i in range(int(search)-1,int(end)-2,-1):
        bot.send_photo(message.chat.id , photo = open("data/"+file[i]+"_thumb.jpg" , "rb") , caption=" {} : ".format(i+1) + "\n" + "total used : {}".format(amount[i]))
        sleep(2)


# specific sticker count
@bot.message_handler(commands="check")
def sticker(message):
    bot.register_next_step_handler(bot.reply_to(message , 'Pls enter the number'), sticker_check)

def sticker_check(message):
    f = open('data\\result.json','r',encoding="utf-8")
    data = json.load(f)
    search = message.text
    list = []
    name = []
    count = 0 
    for msg in data["messages"]:
        if msg["type"] != "message":
            continue
        try:
            if msg["media_type"] == "sticker":
                if msg["file"] in name:
                    list[name.index(msg["file"])] += 1 

                else:
                    name.append(msg["file"])
                    list.append(1)
        except:
            pass


    df = DataFrame({'name' : name,
                'amount' : list})

    df = df.nlargest(len(name),'amount')

    file = df['name'].tolist()
    amount = df["amount"].tolist()

    get = file[int(search)-1]
    name2 = []

    count = amount[int(search)-1]

    for msg in data["messages"]:
        if msg["type"] != "message":
            continue
        try:
            if msg["media_type"] == "sticker":
                if msg["file"] == get:
                    if msg["from"] in name2:
                        list[name2.index(msg["from"])] += 1 
                    else:
                        name2.append(msg["from"]) 
        except:
            pass

    for people in name2:
        df = pandas.DataFrame(data["messages"])
        df = df.rename(columns={"from":"name"})
        df = df.query("type == 'message'").query(f"file == '{get}'").query(f"name == '{people}'")
        
        df = df[['date']]
        df['date'] = pandas.to_datetime(df['date'])
        df['count'] = 1
        df = df.resample("D", on='date').agg({'count':'sum'}).reset_index()
        df['sum'] = df['count'].cumsum()
        plt.plot(df["date"] , df["sum"]  , label=people , marker='o')

    
    plt.legend()
    plt.title('Total used of the stickers')
    plt.xlabel('time')
    plt.ylabel('amount')
    plt.gcf().autofmt_xdate()
    plt.savefig('plot.jpg')
    plt.clf()
    bot.send_photo(message.chat.id , photo=open("data/"+get+"_thumb.jpg" , "rb") ,caption = f"Total used time : {count}")
    bot.send_photo(message.chat.id , photo=open("plot.jpg" , "rb"))

    sleep(3)
    if path.exists("plot.jpg"):
        remove("plot.jpg")


# run telebot
asyncio.run(bot.infinity_polling())
