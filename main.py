import telebot
import requests
import json
import datetime
import time
import configparser

# Конфигурация
config = configparser.ConfigParser()
config.read('config.ini')

# Инициализация токена и идентификатора чата из конфигурационного файла
token = telebot.TeleBot(config['telegram']['token'])
id_chat = config['telegram']['chat_id']

# Получение часа и минуты опроса из конфигурационного файла
hour = int(config['telegram']['hour'])
minute = int(config['telegram']['min'])

# Переменные для хранения времени последней отправки опроса, данных о календаре и текущего года
last_time = None
calendarnaya_data = None
this_year = datetime.datetime.now().year


def load_calendar_data(year):
    # Функция для загрузки данных о календаре с сайта
    link = "http://xmlcalendar.ru/data/ru/" + str(year) + "/calendar.json"
    try:
        answer = requests.get(link)
        answer.raise_for_status()
        return json.loads(answer.text)
    except requests.RequestException as e:
        print("Произошла ошибка при получении данных о календаре:", e)
        return None


def is_workday(date):
    # Функция для проверки, является ли день рабочим
    global calendarnaya_data, this_year

    # Проверка, требуется ли загрузка данных о календаре для текущего года
    if calendarnaya_data is None or date.year != this_year:
        calendarnaya_data = load_calendar_data(date.year)
        if calendarnaya_data is None:
            return True

        this_year = date.year

    for month in calendarnaya_data["months"]:
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
    # Обработчик команды для отправки опроса
    global last_time

    now = datetime.datetime.now()
    if is_workday(now.date()) and (last_time is None or now.date() > last_time.date()):
        token.send_poll(
            chat_id=id_chat,
            question='Где Вы сегодня работаете?',
            options=['Офис', 'Дом', 'Объект'],
            is_anonymous=False
        )
        last_time = now


while True:
    now = datetime.datetime.now()
    if now.hour == hour and now.minute == minute and is_workday(now.date()):
        try:
            send_question(None)
        except Exception as e:
            print("Произошла ошибка при отправке опроса:", e)
            continue

    # Проверка смены года для обновления календарных данных
    if now.year != this_year:
        this_year = now.year
        calendarnaya_data = load_calendar_data(this_year)

    time.sleep(30)
