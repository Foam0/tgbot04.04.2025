import datetime
import time as secs
from bisect import bisect_right

import telebot

from get import get


def next(user: dict, bot: telebot.TeleBot):
    group0 = user['class']
    if group0 == "NO":
        bot.send_message(user['tgid'], "напиши /reg")
        return 0
    s = get((datetime.datetime.today().weekday() + 1) % 7, group0, "group")
    mas = ''
    now = ((secs.time() + 3600 * 5) % 86400)
    mas0 = [32400, 35400, 38700, 42000, 45300, 48900, 52500]
    now = bisect_right(mas0, now) + 1

    xxxxx = max(s.keys()) + 1
    for i in range(xxxxx, 20):
        s[i][1] = {"subject": "go sleep", "teacher": "bed",
                   "auditory": "home"}
        s[i][2] = {"subject": "go sleep", "teacher": "bed",
                   "auditory": "home"}
    xxxxx = min(s.keys()) - 1
    for i in range(-10, xxxxx):
        s[i][1] = {"subject": "get up", "teacher": "bed",
                   "auditory": "home"}
        s[i][2] = {"subject": "go sleep", "teacher": "bed",
                   "auditory": "home"}
    mas += str(s[now][1]["subject"]) + '|' + str(s[now][1]["teacher"]) + '|' + str(s[now][1]["auditory"]) + '\n'
    if s[now][1] != s[now][2]:
        mas += str(s[now][2]["subject"]) + ' ' + str(s[now][2]["teacher"]) + ' ' + str(s[now][2]["auditory"])

    bot.send_message(user['tgid'], mas)
