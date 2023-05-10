import telebot
import requests
import json
import datetime
import time
import configparser

# конфиг
config = configparser.ConfigParser()
config.read('config.ini')

#токены тг
token = telebot.TeleBot(config['telegram']['token'])
id_chat = config['telegram']['chat_id']
#время отправки
hour = int(config['telegram']['hour'])
minute = int(config['telegram']['min'])

last_sent_time = None #отслеживает время последней отправки опроса
calendar_data = None # хранит данные о календаре с информацией о рабочих и нерабочих днях
this_year = datetime.datetime.now().year #текущий год


def is_workday(date):
    global calendar_data, this_year

    if calendar_data is None or date.year != this_year:
        link = "http://xmlcalendar.ru/data/ru/" + str(date.year) + "/calendar.json"
        try:
            answer = requests.get(link)
            answer.raise_for_status()
            calendar_data = json.loads(answer.text)
            this_year = date.year
        except requests.RequestException as e:
            print("Произошла ошибка при получении данных о календаре:", e)
            return True

    for month in calendar_data["months"]:
        if month["month"] == date.month:
            days = month["days"].split(",")
            for day in days:
                day = day.strip("+*")
                if str(date.day) == day:
                    return False
            return True
    return True


@token.message_handler(commands=['question'])
def send_question(message):
    global last_sent_time

    now = datetime.datetime.now()
    if is_workday(now.date()) and (last_sent_time is None or now.date() > last_sent_time.date()):
        token.send_poll(
            chat_id=id_chat,
            question='Где Вы сегодня работаете?',
            options=['Офис', 'Дом', 'Объект'],
            is_anonymous=False
        )
        last_sent_time = now


while True:
    now = datetime.datetime.now()
    if now.hour == hour and now.minute == minute and is_workday(now.date()):
        try:
            send_question(None)
        except Exception as e:
            print("Произошла ошибка при отправке опроса:", e)
            continue
    time.sleep(30)
