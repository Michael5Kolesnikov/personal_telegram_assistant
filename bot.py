import telebot
from telebot import types
from flask import Flask, request

import os
import random

# настройка webhook
from config import TOKEN, secret, url

bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)
app = Flask(__name__)


@app.route('/' + secret, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 2000


# Обработка сообщений
main_buttons = [types.KeyboardButton(button) for button in ('События', 'Заметки', '🎲 Рандомное число', '😊 Как дела?', 'Мои возможности')]


@bot.message_handler(commands=['start'])  # обработка сообщения '/start' при первом запуске. Пявление главных кнопок
def welcome(message: types.Message):
    id_ = message.from_user.id
    # если пользователь первый раз написал команду '/start', то добавляем его id в список_id (это Data_clients) наших пользователей
    if f'{id_}' not in os.listdir('Data_clients'):
        os.mkdir(f'Data_clients//{id_}')
        os.mkdir(f'Data_clients//{id_}//События')
        os.mkdir(f'Data_clients//{id_}//Заметки')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*main_buttons)
    bot.send_message(message.chat.id,
                     f'Приветствую тебя, {message.from_user.first_name}!\nЯ - {bot.get_me().first_name}, бот, созданный, чтобы быть тебе полезным.',
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def answer(message: types.Message):
    if message.chat.type == 'private':
        if message.text == 'События' or message.text == 'Заметки':
            markup = types.InlineKeyboardMarkup(row_width=3)
            create = types.InlineKeyboardButton('Создать', callback_data=f'create_{message.text}')
            look = types.InlineKeyboardButton('Посмотреть', callback_data=f'look_{message.text}')
            delete = types.InlineKeyboardButton('Удалить', callback_data=f'delete_{message.text}')
            markup.add(create, look, delete)
            bot.send_message(message.chat.id, 'Что хотите сделать?', reply_markup=markup)

        elif message.text == '🎲 Рандомное число':
            bot.send_message(message.chat.id, str(random.randint(0, 1000)))

        elif message.text == '😊 Как дела?':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
            item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)

        elif message.text == 'Мои возможности':
            bot.send_message(message.chat.id,
                             '1. Создание/удаление события – дата, время, заголовок события, описание события, время напоминания \n'
                             '2. Напоминание о событие – выводится время события и описание события\n'
                             '3. Вызов списка запланированных событий (дата, время, заголовки)\n'
                             '4. Создание/удаление заметок\n'
                             '5. Вызов списка заметок (заголовки)\n'
                             '6. Вызов отдельной заметки\n'
                             '7. Сгенерировать случайное число от 0 до 1000')

        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить 😢')


path = ''  # для путей создаваемых файлов и папок
kind = ''  # для разделения событий и заметок между собой


def write_down(path_, text):
    f = open(path_, 'a')
    f.write(text + '\n')
    f.close()


def name(message: types.Message):  # обработка названий событий и заметок
    global path, kind
    id_ = message.from_user.id

    # если события или заметки с таким же названием еще нет, то создаем новую
    if message.text not in os.listdir(f'Data_clients//{id_}//{kind}'):
        path = f'Data_clients//{id_}//{kind}//{message.text}.txt'
        f = open(path, 'w')
        f.write(message.text + '\n')
        f.close()
        if kind == 'События':
            msg = bot.send_message(message.chat.id, 'Введите дату события:')
            bot.register_next_step_handler(msg, date)
        else:
            msg = bot.send_message(message.chat.id, 'Введите содержание заметки:')
            bot.register_next_step_handler(msg, description)
    else:
        bot.send_message(message.chat.id, 'Извините. Вы уже использовали такое название!')


def date(message: types.Message):
    global path
    write_down(path, message.text)
    msg = bot.send_message(message.chat.id, 'Введите время события:')
    bot.register_next_step_handler(msg, time)


def time(message: types.Message):
    global path
    write_down(path, message.text)
    msg = bot.send_message(message.chat.id, 'Введите описание события:')
    bot.register_next_step_handler(msg, description)


def description(message: types.Message):  # описание события или заметки
    global path
    write_down(path, message.text)
    if kind == 'События':
        msg = bot.send_message(message.chat.id, 'Введите время напоминания четко в формате год.месяц.день.час.минута\n'
                                                'Пример - 2021.01.01.09.30\n'
                                                'Если вам не нужно напоминание, то вы можете пропустить этот шаг написав цифру 0')
        bot.register_next_step_handler(msg, time_of_remaining)
    else:
        bot.send_message(message.chat.id, 'Заметка успешно создана!')


def time_of_remaining(message: types.Message):
    global path
    text = message.text
    time_remain = text[0:4] + text[5:7] + text[8:10] + text[11:13] + text[14:]
    if time_remain.isdigit() and len(text) == 16:
        write_down(path, message.text)
        bot.send_message(message.chat.id, 'Событие успешно создано!')
        f = open(f'Remain//{time_remain}.txt', 'w')
        f.close()
        f = open(path)
        write_down(f'Remain//{time_remain}.txt', f'{message.chat.id}\n' + f.read())
        f.close()
    elif text == '0':
        bot.send_message(message.chat.id, 'Событие успешно создано!')
    else:
        msg = bot.send_message(message.chat.id, 'Извините! Вы неверно указали время напоминания!  Введите, пожалуйста, его еще раз')
        bot.register_next_step_handler(msg, time_of_remaining)


@bot.callback_query_handler(func=lambda call: True)  # работа с кнопками под сообщениями
def callback_inline(call):
    global path, kind
    try:
        if call.message:
            id_ = call.message.chat.id
            
            # обработка действий с событиями и заметками
            if 'create' == call.data[0:6]:
                msg = bot.send_message(id_, 'Введите название:')
                kind = call.data[7:]
                bot.register_next_step_handler(msg, name)
            elif 'look' == call.data[0:4]:
                if call.data[5:] == 'События':
                    kind = 'События'
                else:
                    kind = 'Заметки'
                path = f'Data_clients//{id_}//{kind}'
                list_ = os.listdir(path)
                if list_:
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    markup.add(*[types.InlineKeyboardButton(button[:-4], callback_data=str(list_.index(button))) for button in list_])
                    bot.send_message(id_, 'Список:', reply_markup=markup)
                else:
                    bot.send_message(id_, 'Тут еще ничего нет')
            elif 'delete' == call.data[0:6]:
                path = f'Data_clients//{id_}//{call.data[7:]}'  # с помощью call.data выбираем нужную папку(либо События, либо Заметки)
                list_ = os.listdir(path)
                if list_:
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    markup.add(*[types.InlineKeyboardButton(button[:-4], callback_data=str(list_.index(button)) + 'd') for button in list_])
                    # добавляем к callback_data букву d, чтобы потом удалить, а не просмотреть
                    bot.send_message(id_, 'Что хотите удалить?', reply_markup=markup)
                else:
                    bot.send_message(id_, 'Тут еще ничего нет')

            # обработка маленького разговора "Как дела?"
            elif call.data == 'good':
                bot.send_message(id_, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(id_, 'Бывает 😢')

            # вызов или удаление определенного события или заметки
            elif call.data[0].isdigit():
                list_ = os.listdir(path)
                if call.data[-1].isdigit():  # проверяем наличие буквы d
                    path = f'{path}//{list_[int(call.data)]}'
                    f = open(path)
                    bot.send_message(id_, f.read())
                    f.close()
                else:
                    os.remove(f'{path}//{list_[int(call.data[:-1])]}')
                    bot.send_message(id_, 'Удалено успешно!')

            bot.edit_message_text(chat_id=id_, message_id=call.message.message_id, text=call.message.text, reply_markup=None)  # удаление использованной кнопки

    except Exception as e:
        print(repr(e))
