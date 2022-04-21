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
    


# run telebot
asyncio.run(bot.infinity_polling())
