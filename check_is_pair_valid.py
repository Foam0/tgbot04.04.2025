import hashlib
import io
import database

import cv2
import numpy
import requests
from PIL import Image
import shutup


def where(hash_pic):
    for i in range(10):
        file = open(f"{i}.txt", 'r')
        mas = file.readlines()
        if f"{hash_pic.hexdigest()}\n" in mas:
            return i


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


def check(login, password):
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
    if get_token.content == b'none':
        return False
    database.add_login_pass(login, password)
    return True
