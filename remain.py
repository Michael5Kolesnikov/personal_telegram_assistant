import os
from datetime import datetime
import telebot

bot = telebot.TeleBot('1930827544:AAGglpmI2cDO1W_h5tGintjvCE-xPZSR-Co')

while True:
    n = f'{datetime.now()}'
    for i in os.listdir('remain'):
        now = n[0:4] + n[5:7] + n[8:10] + n[11:13] + n[14:16]
        if int(i[:-4]) <= int(now):
            f = open(f'remain//{i}')
            chat_id = f.readline()
            bot.send_message(chat_id, 'Напоминание о событии: \n' + f.read())
            f.close()
            os.remove(f'remain//{i}')
        # if not os.listdir('remain'):
        #     exit()
