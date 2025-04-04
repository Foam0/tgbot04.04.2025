from pymongo.mongo_client import MongoClient
import os
import dotenv

dotenv.load_dotenv()
uri = os.getenv("MONGO_URI")
# Create a new client and connect to the server
client = MongoClient(uri)
db = client.users


def upd_user_login_password(tgid, login, password):
    collection = db.tgid_login_password
    collection.update_one(
        {"tgid": tgid},  # Фильтр для поиска документа
        {"$set": {"login": login, "password": password}},
        upsert=True
    )


def upd_user_class(tgid: int, classid: int):
    collection = db.tgid_login_password
    collection.update_one(
        {"tgid": tgid},  # Фильтр для поиска документа
        {"$set": {"class": classid}},
        upsert=True
    )


def add_login_pass(login, password):
    collection = db.login_password
    result = collection.update_one(
        {'login': login, 'password': password},  # Условие (фильтр)
        {'$setOnInsert': {'login': login, 'password': password}},  # Операция, если документ не найден
        upsert=True  # Создать новый документ, если такого нет
    )


def init_user(tgid: int):
    collection = db.tgid_login_password
    collection.update_one(
        {"tgid": tgid},  # Фильтр для поиска документа
        {"$setOnInsert": {"login": "", "password": "", "reg": 0, "add": 0, "ban": 0, "class": -1}},
        upsert=True
    )


def upd_try_to_reg(tgid: int, flag: bool):
    collection = db.tgid_login_password
    collection.update_one(
        {"tgid": tgid},  # Фильтр для поиска документа
        {"$set": {"reg": flag}},
        upsert=True
    )


def upd_try_to_add(tgid: int, flag: bool):
    collection = db.tgid_login_password
    collection.update_one(
        {"tgid": tgid},  # Фильтр для поиска документа
        {"$set": {"add": flag}},
        upsert=True
    )


def get_login_passwords():
    collection = db.login_password
    return list(collection.find({}))


def get_user(tgid: int):
    init_user(tgid)
    collection = db.tgid_login_password
    return collection.find_one({"tgid": tgid})


def get_users():
    collection = db.tgid_login_password
    return list(collection.find({}))


if __name__ == "__main__":
    # get_user(694191338)
    with open("database.txt") as f:
        x = f.read().strip().split('\n')
        for i in x:
            a, b, c = i.split()
            a = int(a)
            init_user(a)
            upd_user_login_password(a, b, c)
            print(a)
    # with open("login-passwords") as f:
    #     x = f.read().strip().split('\n')
    #     for i in x:
    #         a, b, c = i.split()
    #         a = int(a)
    #         init_user(a)
    #         add_login_pass(a, b)
    #         print(a)
    with open("people.txt") as f:
        x = f.read().strip().split('\n')
        for i in x:
            a, b = i.split(':')
            a = int(a)
            b = int(b)
            init_user(a)
            upd_user_class(a, b)
            print(a)
