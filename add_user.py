import check_is_pair_valid
import database


def add(id, login, password, bot):
    if check_is_pair_valid.check(login, password):
        database.add_login_pass(login, password)
        database.upd_user_login_password(id, login, password)
        bot.send_message(id, "OK")
    else:
        bot.send_message(id, "Неправильный логин/пароль")


if __name__ == '__main__':
    import telebot

    read = open("config.cfg", "r").readlines()
    read[0] = read[0][:-1]
    myid = 694191338
    bot = telebot.TeleBot(read[0])
    while True:
        s = input()
        s = s.split('\n')[0]
        login = s.split()[0]
        password = s.split()[1]
        add(myid, login, password, bot)

