import psycopg2

import datetime
import telebot
from telebot import types



bot = telebot.TeleBot(token)

conn = psycopg2.connect(database="rasp_db",
                        user="postgres",
                        password="123",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

time = ['9:30-11:05', '11:20-12:55', '13:10-14:45', '15:25-17:00', '17:15-18:50']
weekday = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


def get_this_week():
    now = datetime.datetime.now()
    first = datetime.datetime(year=now.year, month=8, day=30)
    return int((now - first).days / 7)


def get_day_number(week_offset, day):
    return ((get_this_week() + week_offset) % 4) * 7 + day + 1


def get_rasp(day_number):
    cursor.execute(f"SELECT * FROM public.rasp_db WHERE id='{day_number}'")
    records = cursor.fetchall()[0][1:]
    msg = f"{weekday[day_number % 7 - 1]}\n"
    for i, record in enumerate(records):
        if record:
            cursor.execute(f"SELECT * FROM public.pars WHERE id='{record}'")
            records = cursor.fetchall()[0][1:]
            msg += f"{i + 1}. {time[i]}: {records[0]} - {records[1]} - {records[2]}"
        else:
            msg += f"{i + 1}. {time[i]}: Нет пары"
        msg += '\n'
    return msg


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Хочу")
    bot.send_message(message.chat.id, 'Здравствуйте! Хотите узнать свежую информацию о ВУЗе или расписании?',
                     reply_markup=keyboard)


@bot.message_handler(commands=['mtuci'])
def answer_mtuci(message):
    bot.send_message(message.chat.id, 'Вам сюда – https://mtuci.ru/')


@bot.message_handler(commands=['week'])
def answer_mtuci(message):
    bot.send_message(message.chat.id, ['Сейчас четная неделя', 'Сейчас нечетная неделя'][(get_this_week() + 1) % 2])


@bot.message_handler(commands=['help'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/rasp', '/week', '/mtuci')
    bot.send_message(message.chat.id, 'Я - бот группы БИН2004 и умею:\n'
                                      'При использовании команды /rasp вывожу информацию с расписанием на выбранный '
                                      'день текущей недели.\n'
                                      'При использовании команды /week вывожу какая на данный момент неделя – '
                                      'верхняя/нижняя.\n'
                                      'При использовании команды /mtuci можно перейти на сайт ВУЗа!',
                     reply_markup=markup)


@bot.message_handler(commands=['rasp'])
def rasp_message(message):
    button1 = types.KeyboardButton('Понедельник')
    button2 = types.KeyboardButton('Вторник')
    button3 = types.KeyboardButton('Среда')
    button4 = types.KeyboardButton('Четверг')
    button5 = types.KeyboardButton('Пятница')
    button6 = types.KeyboardButton('Суббота')
    button7 = types.KeyboardButton('Расписание на текущую неделю')
    button8 = types.KeyboardButton('Расписание на следующую неделю')
    markup2 = types.ReplyKeyboardMarkup().row(button1, button2, button3).row(button4, button5, button6).row(
        button7, button8)
    bot.send_message(message.chat.id, 'Выберите день недели. \n'
                                      'При нажатии на кнопку "Расписание на текущую неделю" вывожу информацию с '
                                      'расписанием на всю текущую неделю.\n '
                                      'При нажатии на кнопку "Расписание на следующую неделю" вывожу информацию с '
                                      'расписанием на всю следующую неделю.\n ', reply_markup=markup2)


@bot.message_handler(content_types=['text'])
def start_message(message):
    nom = -1
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/rasp', '/week', '/mtuci')
    if message.text.lower() == "хочу":
        bot.send_message(message.chat.id, 'Я - бот группы БИН2004 и умею:\n'
                                          'При использовании команды /rasp вывожу информацию с расписанием на выбранный'
                                          ' день текущей недели.\n'
                                          'При использовании команды /week вывожу какая на данный момент неделя – '
                                          'верхняя/нижняя.\n'
                                          'При использовании команды /mtuci можно перейти на сайт ВУЗа!',
                         reply_markup=markup)
        return
    elif message.text.lower() == "понедельник":
        nom = 0
    elif message.text.lower() == "вторник":
        nom = 1
    elif message.text.lower() == "среда":
        nom = 2
    elif message.text.lower() == "четверг":
        nom = 3
    elif message.text.lower() == "пятница":
        nom = 4
    elif message.text.lower() == "суббота":
        nom = 5
    elif message.text.lower() == "расписание на текущую неделю":
        msg = ''
        for i in range(0, 6):
            msg += get_rasp(get_day_number(0, i)) + '\n'
        bot.send_message(message.chat.id, msg)
        return
    elif message.text.lower() == "расписание на следующую неделю":
        msg = ''
        for i in range(0, 6):
            msg += get_rasp(get_day_number(1, i)) + '\n'
        bot.send_message(message.chat.id, msg)
        return
    if nom == -1:
        bot.send_message(message.chat.id, 'Извините, я Вас не понял')
    else:
        bot.send_message(message.chat.id, get_rasp(get_day_number(0, nom)))


bot.infinity_polling()
