import random
import bs4
import requests
import dotenv
import os

dotenv.load_dotenv()


# Replace with your API endpoint and authentication details
def gen_num(length=30):
    ans = ''
    for i in range(length):
        ans += str(random.randint(0, 9))
    return ans


def gen(solution: str, num: str, lang_id: int):
    ret = f'-----------------------------{num}\n\
Content-Disposition: form-data; name="lang_id"\n\
\n\
{lang_id}\n\
-----------------------------{num}\n\
Content-Disposition: form-data; name="course_id"\n\
\n\
34\n\
-----------------------------{num}\n\
Content-Disposition: form-data; name="file"; filename="third.txt"\n\
Content-Type: text/plain\n\n'
    ret += solution
    ret += '\n'
    ret += f'-----------------------------{num}--\n'
    return ret


"""headers"""
headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
}

"""my_session"""
cookie_mine = {
    "MoodleSession": "123"
}
"""teachers_session"""
cookie_teacher = {
    "MoodleSession": "123"
}


def init(login, password, login_t, password_t):
    global cookie_mine
    global cookie_teacher
    loginurl = "https://informatics.msk.ru/login/index.php"
    session = requests.Session()
    x = session.get(loginurl, headers=headers)
    logintoken = bs4.BeautifulSoup(x.content).find_all("input")[5]['value']
    data = {
        "logintoken": logintoken,
        "username": login,
        "password": password
    }
    x = session.post(loginurl, data=data,
                     headers=headers, allow_redirects=False)
    # print(x.cookies.keys())
    x = session.get("https://informatics.msk.ru/", headers=headers)
    cookie_mine = {"MoodleSession": session.cookies["MoodleSession"]}

    loginurl = "https://informatics.msk.ru/login/index.php"
    session = requests.Session()
    x = session.get(loginurl, headers=headers)
    logintoken = bs4.BeautifulSoup(x.content).find_all("input")[5]['value']
    data = {
        "logintoken": logintoken,
        "username": login_t,
        "password": password_t
    }
    x = session.post(loginurl, data=data,
                     headers=headers, allow_redirects=False)
    # print(x.cookies.keys())
    x = session.get("https://informatics.msk.ru/", headers=headers)
    cookie_teacher = {"MoodleSession": session.cookies["MoodleSession"]}


def send_sol_id(solution: str, chapterid: str, lang_id: int):
    nn = gen_num()
    prog = gen(solution, nn, lang_id).replace('﻿', '')
    headers2 = {
        "Content-Type": f"multipart/form-data; boundary=---------------------------{nn}",
        "Content-Length": str(len(prog)),

    }
    zxc = requests.post(f"https://informatics.msk.ru/py/problem/{chapterid}/submit", headers=headers2,
                        cookies=cookie_mine,
                        data=prog.encode("utf-8"))
    # gen(solution, nn, lang_id).replace('﻿', '')
    print(zxc)


def get_solution(chapterid):
    data = requests.get(
        f"https://informatics.msk.ru/py/problem/{chapterid}/filter-runs?problem_id={chapterid}&from_timestamp=-1&to_timestamp=-1&user_id=0&lang_id=-1&status_id=-1&statement_id=0&count=20&with_comment=&page=1",
        cookies=cookie_teacher, headers=headers)
    data = data.json()
    for i in sorted(data['data'], key=lambda x: x['ejudge_language_id'] == 27):
        if i['ejudge_score'] == 100:
            good_solve = requests.post(f"https://informatics.msk.ru/py/problem/run/{i['id']}/source",
                                       cookies=cookie_teacher, headers=headers)
            return [good_solve.json()['data']['source'], good_solve.json()['data']['language_id']]
    assert False


def solve(task_id: str):
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    t_user = os.getenv("T_USER")
    t_pass = os.getenv("T_PASS")
    init(username, password, t_user, t_pass)
    a, b = get_solution(task_id)
    send_sol_id(a, task_id, b)


if __name__ == "__main__":
    solve("1086")
