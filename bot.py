import telebot
import config
from telebot import types
import random

bot = telebot.TeleBot(config.TOKEN)
events = []  # события пользователя
event = {}  # переменная для вносимых событий
notes = []  # заметки пользователя
notes_name = []  # названия заметок пользователя


@bot.message_handler(commands=['start'])  # обработка сообщения '/start' при первом запуске. Пявление главных кнопок
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_buttons = [types.KeyboardButton(button) for button in ('Новое событие', 'Список событий',
                                                                'Новая заметка', 'Список заметок', 'Вызвать заметку',
                                                                '🎲 Рандомное число', '😊 Как дела?',
                                                                'Мои возможности')]
    markup.add(*main_buttons)
    bot.send_message(message.chat.id,
                     f'Приветствую тебя, {message.from_user.first_name}!\nЯ - {bot.get_me().first_name}, бот, созданный, чтобы быть тебе полезным.',
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def answer(message):
    global events
    if message.chat.type == 'private':
        if message.text == 'Новое событие':
            msg = bot.send_message(message.chat.id, 'Введите дату в формате:\nдень:месяц:год')
            bot.register_next_step_handler(msg, date)

        elif message.text == 'Список событий':
            bot.reply_to(message, 'Ваш список событий:')
            all_items = ''
            for event_ in events:
                for item in event_:
                    all_items += f'{item} : {event_[item]}' + '\n'
                bot.send_message(message.chat.id, all_items)
                all_items = ''

        elif message.text == 'Новая заметка':
            msg = bot.send_message(message.chat.id, 'Введите название заметки:')
            bot.register_next_step_handler(msg, name_note)

        elif message.text == 'Список заметок':
            bot.send_message(message.chat.id, '\n'.join(notes_name))

        elif message.text == 'Вызвать заметку':
            markup = types.InlineKeyboardMarkup(row_width=2)
            notes_buttons = [types.InlineKeyboardButton(button, callback_data=str(notes_name.index(button))) for button in notes_name]
            markup.add(*notes_buttons)
            bot.send_message(message.chat.id, 'Какую заметку хотите просмотреть?', reply_markup=markup)

        elif message.text == '🎲 Рандомное число':
            bot.send_message(message.chat.id, str(random.randint(0, 100)))

        elif message.text == '😊 Как дела?':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
            item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)

        elif message.text == 'Мои возможности':
            bot.send_message(message.chat.id, '1. Создание события – дата, время, заголовок события, описание события, время напоминания \n'
                                              '2. Напоминание о событие – выводится время события и описание события\n'
                                              '3. Вызов списка запланированных событий (дата, время, заголовки)\n'
                                              '4. Создание заметок\n'
                                              '5. Вызов списка заметок (заголовки)\n'
                                              '6. Вызов отдельной заметки\n'
                                              '7. Сгенерировать случайное число от 0 до 100')

        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить 😢')


# работа с заметками
def name_note(message):
    global notes_name
    if message.text not in notes_name:
        notes_name.append(message.text)
    else:
        bot.send_message(message.chat.id, 'Уже есть заметка с таким именем!')
        return
    msg = bot.send_message(message.chat.id, 'Введите содержание заметки:')
    bot.register_next_step_handler(msg, text_note)


def text_note(message):
    global notes
    notes.append(message.text)


# работа с событиями
def date(message):
    global event
    event = {'Дата': message.text}
    msg = bot.send_message(message.chat.id, 'Введите время в формате:\nчас:минуты')
    bot.register_next_step_handler(msg, time)


def time(message):
    global event
    event.update({'Время': message.text})
    msg = bot.send_message(message.chat.id, 'Введите название события:')
    bot.register_next_step_handler(msg, name)


def name(message):
    global event
    event.update({'Название': message.text})
    msg = bot.send_message(message.chat.id, 'Введите описание события: (по желанию)')
    bot.register_next_step_handler(msg, description)


def description(message):
    global event
    if description:
        event.update({'Описание': message.text})
    msg = bot.send_message(message.chat.id, 'Введите время напоминания в формате час:минута:день:месяц:год')
    bot.register_next_step_handler(msg, time_of_remaining)


def time_of_remaining(message):
    global event
    event.update({'Время напоминания': message.text})
    events.append(event)


@bot.callback_query_handler(func=lambda call: True)  # работа с кнопками под сообщениями
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')
            elif call.data.isdigit():  # вызов определенной заметки
                bot.send_message(call.message.chat.id, notes[int(call.data)])
    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)  # запуск
