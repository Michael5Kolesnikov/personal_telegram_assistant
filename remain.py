import os
from datetime import datetime

import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

while True:
    n = f'{datetime.now()}'
    for i in os.listdir('Remain'):
        now = n[0:4] + n[5:7] + n[8:10] + n[11:13] + n[14:16]
        if int(i[:-4]) <= int(now):
            f = open(f'Remain//{i}')
            chat_id = f.readline()
            bot.send_message(chat_id, 'Напоминание о событии: \n' + f.read())
            f.close()
            os.remove(f'Remain//{i}')
