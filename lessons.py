import asyncio
import concurrent.futures
import copy
import hashlib
import io
import json
import time

import cv2
import numpy
import requests
import telebot
import urllib3
from PIL import Image
from tabulate import tabulate

from functools import lru_cache
import database

urllib3.disable_warnings()


def init_subjects(token, login):
    init = (requests.get("https://lycreg.urfu.ru/js/ini.js", verify=False).content.decode())
    init = init[init.find("subjDef"):]
    init = init[:init.find("}")]
    init = init[init.find("{") + 1:]
    d = dict()
    init = list(init.split(','))
    for i in range(len(init)):
        now = list(init[i].split(':'))
        now[1] = now[1][1:-1]
        d[now[0]] = now[1]
    data = {"t": "pupil",
            "l": login,
            "p": token,
            "f": "subjList"
            }
    x = requests.post("https://lycreg.urfu.ru/", json=data, verify=False).content.decode()
    x = x[1:-1]
    for i in x.split(','):
        j = i.split(':')
        j[0] = j[0][1:-1]
        j[1] = j[1][1:-1]
        d[j[0]] = j[1]
    return d


def init_teachers(token, login):
    # init = (requests.get("https://lycreg.urfu.ru/js/ini.js", verify=False).content.decode())
    # init = init[init.find("subjDef"):]
    # init = init[:init.find("}")]
    # init = init[init.find("{") + 1:]
    d = dict()
    # init = list(init.split(','))
    # for i in range(len(init)):
    #     now = list(init[i].split(':'))
    #     now[1] = now[1][1:-1]
    #     d[now[0]] = now[1]
    data = {"t": "pupil",
            "l": login,
            "p": token,
            "f": "teachList"
            }
    x = requests.post("https://lycreg.urfu.ru/", json=data, verify=False).content.decode()
    x = json.loads(x)
    d = dict()
    for i in x:
        d[i["login"]] = i["fio"]
    return d


def date_to_normal(s: str) -> str:
    month = int(s[1])
    day = int(s[3]) + int(s[2]) * 10
    month = (month + 9) % 12
    if month == 0:
        month = 12
    return f"{'0' * (2 - len(str(day)))}{day}.{'0' * (2 - len(str(month)))}{month}"


def less_eq_date(date1: str, date2: str) -> bool:
    if date1.count('d'): date1 = date_to_normal(date1)
    if date2.count('d'): date2 = date_to_normal(date2)
    return date1.split('.')[::-1] < date2.split('.')[::-1]


def solve_i_num(image):
    open_cv_image = image
    leftj = 1e9
    rightj = 0
    upi = 1e9
    downi = 0
    for i in range(30):
        for j in range(20):
            if open_cv_image[i, j] == 0:
                leftj = min(leftj, j)
                rightj = max(rightj, j)
                upi = min(upi, i)
                downi = max(downi, i)
    open_cv_image = open_cv_image[upi:downi + 1, leftj:rightj + 1]
    hash_pic = hashlib.sha1(numpy.array(open_cv_image))
    return where(hash_pic)


def where(hash_pic):
    for i in range(10):
        file = open(f"{i}.txt", 'r')
        mas = file.readlines()
        if f"{hash_pic.hexdigest()}\n" in mas:
            return i


def get_hm(login, password):
    url = "https://lycreg.urfu.ru/cpt.a"
    x = requests.get(url, verify=False)
    pic = Image.open(io.BytesIO(x.content)).convert("RGB")
    open_cv_image = numpy.array(pic)
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    ret, open_cv_image = cv2.threshold(gray_image, 200, 255, 0)
    solved_cpt = ''
    for i in range(6):
        solved_cpt += str(solve_i_num(open_cv_image[0:30, 0 + i * 20:20 + 20 * i + 1]))
    cpt_id = x.headers["X-cpt"]
    new_url = 'https://lycreg.urfu.ru/'
    user = {
        'c': solved_cpt,
        'ci': cpt_id,
        'f': 'login',
        'l': login,
        'p': password,
        't': 'pupil'
    }
    get_token = requests.post(new_url, json=user, verify=False)
    data = json.loads(get_token.content)  # string to jsonpass
    token = (data['token'])
    data = {
        "f": "jrnGet",
        "l": login,
        "p": token,
        "t": "pupil",
        "z": []
    }
    subj = requests.post(new_url, json=data, verify=False).content.decode()
    code2namesubj = init_subjects(token, login)

    subj = json.loads(subj)
    ans = ""
    for i in sorted(list(subj)):
        name = copy.copy(i)
        name = code2namesubj[name.split("_")[1]]
        # print(name)
        ans += f"**{name}**\n"
        tasks = sorted(list(subj[i]))
        tasks.reverse()
        for num in tasks:
            if len(subj[i][num][0]) != 0:
                ans += str(date_to_normal(num)) + ' ' + str(subj[i][num][0]) + '\n'
                break
        for num in tasks:
            if len(subj[i][num][1]) != 0:
                ans += str(date_to_normal(num)) + ' ' + str(subj[i][num][1])
                break
        ans += '\n' + '\n'
    # print(ans)
    return ans


def get_marks(login, password):
    url = "https://lycreg.urfu.ru/cpt.a"
    x = requests.get(url, verify=False)
    pic = Image.open(io.BytesIO(x.content)).convert("RGB")
    open_cv_image = numpy.array(pic)
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    ret, open_cv_image = cv2.threshold(gray_image, 200, 255, 0)
    solved_cpt = ''
    for i in range(6):
        solved_cpt += str(solve_i_num(open_cv_image[0:30, 0 + i * 20:20 + 20 * i + 1]))
    cpt_id = x.headers["X-cpt"]
    new_url = 'https://lycreg.urfu.ru/'
    user = {
        'c': solved_cpt,
        'ci': cpt_id,
        'f': 'login',
        'l': login,
        'p': password,
        't': 'pupil'
    }
    get_token = requests.post(new_url, json=user, verify=False)
    data = json.loads(get_token.content)  # string to jsonpass
    token = (data['token'])
    data = {
        "f": "jrnGet",
        "l": login,
        "p": token,
        "t": "pupil",
        "z": []
    }
    subj = requests.post(new_url, json=data, verify=False).content.decode()
    code2namesubj = init_subjects(token, login)
    code2nametecher = init_teachers(token, login)
    STPER = [["1ч", "Первая четверть", "01.09", "05.11"],
             ["2ч", "Вторая четверть", "06.11", "31.12"],
             ["3ч", "Третья четверть", "01.01", "28.03"],
             ["4ч", "Четвертая четверть", "29.03", "31.05"]]

    roleNames = {
        "root": "Гл. администратор",
        "admin": "Администратор",
        "teacher": "Учитель",
        "tutor": "Кл. руководитель",
        "pupil": "Учащийся",
        "parent": "Родитель"
    }
    subj = json.loads(subj)
    # Your JSON data
    data = subj

    # Create a list of lists for the table
    table_data = [["Предмет, учитель", "1ч", "2ч", "3ч", "4ч"]]
    # Loop through the data and add rows to the table_data
    for key, value in sorted(data.items(), key=lambda x: [x[0].split('_')[0], x[0].split('_')[1]]):
        subject_teacher = code2nametecher[key.split("_")[-1]]
        subject_name = code2namesubj[key.split("_")[1]]
        marks = [[], [], [], []]
        for [day, inf] in sorted(value.items(), key=lambda x: date_to_normal(x[0]).split('.')[::-1]):
            if len(inf) >= 4:
                for i in range(4):
                    if less_eq_date(STPER[i][2], day) and less_eq_date(day, STPER[i][3]):
                        # marks[i].append(f"{inf[2]} : {inf[3]}")
                        marks[i].append(f"{inf[3]}")
        table_data.append(
            [f'{subject_name}\n{subject_teacher}', ' '.join(marks[0]), ' '.join(marks[1]), ' '.join(marks[2]),
             ' '.join(marks[3])])

        # row = [value["d106"][0], value["d022"][0], value["d015"][0], value["d029"][0]]
        # table_data.append([subject_teacher] + row)

    # Create a table using tabulate
    table = tabulate(table_data, headers="firstrow", tablefmt="grid", stralign='left')

    # Print the HTML table
    print(table)
    table = f"Если криво отображается поверните телефон \n<pre>{table}</pre>"

    return table
    # return ans


if __name__ == "__main__":
    get_marks("", "")


@lru_cache(maxsize=200)
def how_many_truancys(login, password, curtime: int):
    for i in range(5):
        try:
            print(login)
            url = "https://lycreg.urfu.ru/cpt.a"
            x = requests.get(url, verify=False)
            pic = Image.open(io.BytesIO(x.content)).convert("RGB")
            open_cv_image = numpy.array(pic)
            gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            ret, open_cv_image = cv2.threshold(gray_image, 200, 255, 0)
            solved_cpt = ''
            for i in range(6):
                solved_cpt += str(solve_i_num(open_cv_image[0:30, 0 + i * 20:20 + 20 * i + 1]))
            cpt_id = x.headers["X-cpt"]
            new_url = 'https://lycreg.urfu.ru/'
            user = {
                'c': solved_cpt,
                'ci': cpt_id,
                'f': 'login',
                'l': login,
                'p': password,
                't': 'pupil'
            }
            get_token = requests.post(new_url, json=user, verify=False)
            data = json.loads(get_token.content)  # string to jsonpass
            token = (data['token'])
            data = {
                "f": "absentGet",
                "l": login,
                "p": token,
                "t": "pupil",
                "z": ["", login]
            }
            subj = requests.post(new_url, json=data, verify=False).content.decode()
            code2namesubj = init_subjects(token, login)
            subj = json.loads(subj)
            cnt = 0
            set1 = set()
            for zxc in subj:
                cnt += int(zxc["abs"])
                set1.add(zxc["d"])
            print(login)
            return [login, cnt, len(set1)]
        except:
            print(login, f"error {i}")


# mas = []
# for i in open("login-passwords").readlines():
#     print(i.split()[0], how_many_truancys(i.split()[0], i.split()[1]))
#     mas.append([i.split()[0], how_many_truancys(i.split()[0], i.split()[1])])
# mas.sort(key=lambda x: x[1])
# print(*mas, sep='\n')


async def work(mas: list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                how_many_truancys,
                i['login'], i['password'], time.time_ns() // int(1e13)
            )
            for i in database.get_login_passwords()
        ]
        for response in await asyncio.gather(*futures):
            print(response)
            mas.append(response[:])


def send_long_message(chat_id: str, message: str, bot: telebot.TeleBot):
    first = f"Если криво отображается поверните телефон \n"
    # <pre>{message}</pre>
    parts = [first]
    cur = ''
    lines = message.split('\n')
    lines.append('-' * 10000)
    for i in lines:
        if len(cur + i) >= 3900:
            parts[-1] += f'<pre>{cur}</pre>'
            cur = ''
            parts.append('')
        cur += i + '\n'
    parts.pop()
    for elem in parts:
        bot.send_message(chat_id, elem, parse_mode="html")


def get_razdolbai(user: dict, bot: telebot.TeleBot):
    mas = []
    your_login = user['login']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work(mas))
    loop.close()
    mas.sort(key=lambda x: x[1])
    mas.reverse()
    for i in range(len(mas)):
        if mas[i][0] == your_login:
            mas[i][0] = "вы"
        mas[i] = [i + 1] + mas[i]
    message = (
        tabulate(mas, headers=["номер", "кто", "пропуски", "уникальные дни"], stralign='left', tablefmt="pretty"))
    print(message)
    send_long_message(user['tgid'], message, bot)
    # message = f"Если криво отображается поверните телефон \n<pre>{message}</pre>"
    # bot.send_message(str(chat_id), message, parse_mode="html")
# read = open("config.cfg", "r").readlines()
# read[0] = read[0][:-1]
# myid = 694191338
# bot = telebot.TeleBot(read[0])
# get_razdolbai(myid, bot)
