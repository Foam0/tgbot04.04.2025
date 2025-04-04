import datetime

import telebot

from get import get


def rasp(chat_id: int, text: str, bot: telebot.TeleBot, group0: int, type_g: str):
    weekdays = ["Понедельник\n", "Вторник\n", "Среда\n", "Четверг\n", "Пятница\n", "Суббота\n", "Воскресенье\n"]
    mas = ''
    if group0 == -1:
        bot.send_message(chat_id, "напиши /reg")
        return 0
    if text == "/tomorrow":
        if (datetime.datetime.today().weekday() + 2) % 7 == 0:
            bot.send_message(chat_id, "Воскресенье")
            return 0
        s = get((datetime.datetime.today().weekday() + 2) % 7, group0, type_g)
        mas += weekdays[(datetime.datetime.today().weekday() + 1) % 7]
    else:
        if (datetime.datetime.today().weekday() + 1) % 7 == 0:
            bot.send_message(chat_id, "Воскресенье")
            return 0
        s = get((datetime.datetime.today().weekday() + 1) % 7, group0, type_g)
        mas += weekdays[(datetime.datetime.today().weekday()) % 7]
    if s == "None":
        mas += "Нет уроков"
        bot.send_message(chat_id, mas)
        return "Нет уроков"
    for i in sorted(s.keys()):
        mas += str(i) + ')'
        for j in sorted(s[i]):
            if (j == 1 or s[i][j - 1] != s[i][j]):
                mas += str(s[i][j]["subject"]) + '-' + s[i][j]['auditory'] + ' '
                #
        mas += '\n'
    bot.send_message(chat_id, mas)
