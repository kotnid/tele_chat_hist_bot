import configparser
from logging import info , basicConfig , INFO
from telebot import TeleBot
import asyncio


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


# run telebot
asyncio.run(bot.infinity_polling())
