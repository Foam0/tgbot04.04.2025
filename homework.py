import lessons


def get(user: dict):
    login = user['login']
    password = user['password']
    if login == '':
        return "Вас нет в базе данных добавье себя введя '/add login password'"
    return lessons.get_hm(login, password)


def get_marks(user: dict):
    login = user['login']
    password = user['password']
    if login == '':
        return "Вас нет в базе данных добавье себя введя '/add login password'"
    return lessons.get_marks(login, password)
