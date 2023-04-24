import telebot
import requests
import json
import datetime
import time

#Задаем токен
token = telebot.TeleBot("token")

def is_workday(date):
    link = "http://xmlcalendar.ru/data/ru/" + str(date.year) + "/calendar.json" #ссылка
    dan = requests.get(link) #получаем данные
    inf = json.loads(dan.text) #преобразуем в json
    for month in inf["months"]: #проверка на рабочий день
        if month["month"] == date.month:
            days = month["days"].split(",")
            for day in days:
                if day.endswith("+") or day.endswith("*"): #проверяем на лишние символы * and +
                    day = day.strip("+*") #удаляем лишние символы
                if str(date.day) == day:
                    return False
            return True
    return True


@token.message_handler(commands=['question'])
def send_question(message): #функция отправки опроса
    if is_workday(datetime.datetime.now().date()):
        token.send_poll(chat_id='id',
                        question='Где Вы сегодня работаете?',
                        options=['Офис', 'Дом', 'Объект'],
                        is_anonymous=False)


while True:
    now = datetime.datetime.now() #проверяем время
    if now.hour == 8 and now.minute == 0 and is_workday(now.date()):
        try:
            token.send_poll(chat_id='id',
                            question='Где Вы сегодня работаете?',
                            options=['Офис', 'Дом', 'Объект'],
                            is_anonymous=False)
            time.sleep(60) #ожидание в минуту перед следующей проверкой времени
        except Exception as e:
            print("Произошла ошибка:", e)
            continue
        time.sleep(60) #ожидание в минуту
