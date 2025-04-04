# from lxml import *
import database


def get_id(text):
    file = open("classes2id")
    file = file.readlines()
    print(file)
    for i in file:
        x = i[:-1]
        x = x.split()
        if x[0] == text:
            return x[1]
    return ''


def reg(message, bot, state=1):
    if state == 1:
        bot.send_message(message.chat.id, "Введите ваш класс в формате 8Б")
        database.upd_try_to_reg(message.from_user.id, True)
    else:
        message.text = str(message.text).upper()
        group = get_id(message.text)
        if len(group) == 0:
            bot.send_message(message.chat.id,
                             "Скорее всего ваш класс уже расформирован. Можете не приходить в СУНЦ.")
        else:
            database.upd_try_to_reg(message.from_user.id, False)
            database.upd_user_class(message.from_user.id, int(group))
            bot.send_message(message.chat.id, "Успешная регистрация")
# pyinstaller -F --add-data "people.txt;." --add-data "people.txt;." tg.py
