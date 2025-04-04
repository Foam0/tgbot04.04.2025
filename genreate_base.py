import requests
import PIL
import cv2
import io
from PIL import Image
import time
import numpy
import hashlib


def viewImage(image, name_of_window):
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


while True:
    url = "https://lycreg.urfu.ru/cpt.a"
    x = requests.get(url, verify=False)
    pic = Image.open(io.BytesIO(x.content)).convert("RGB")
    open_cv_image = numpy.array(pic)
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    ret, open_cv_image = cv2.threshold(gray_image, 200, 255, 0)
    copy = open_cv_image

    open_cv_image = open_cv_image[0:30, 0:20]
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
    flag = True
    for i in range(10):
        file = open(f"{i}.txt", 'r')
        mas = file.readlines()
        if f"{hash_pic.hexdigest()}\n" in mas:
            flag = False
    print(str(hash_pic.hexdigest()))
    if flag:
        viewImage(open_cv_image, "bebra")
        number = input()
        file = open(f"{number}.txt", 'a')
        file.write(hash_pic.hexdigest())
        file.write('\n')
