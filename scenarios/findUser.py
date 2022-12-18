import database as db
import botCommands as bot

facultyList = ["IITMM"]
directionList = ["FIIT"]


def mess_about_user(userData):
    username = userData[0][1]
    data = userData[0][2]
    faculty = facultyList[userData[0][7]]
    direction = directionList[userData[0][8]]
    course = userData[0][9]

    msg = f"""Имя пользователя: *{username}*
Дата регистрации: *{data}*
Факультет: *{faculty}*
Направление: *{direction}*
Курс: *{course}*"""
    return msg


def switch_fun(findString, chat_id):
    clear_find_string = str(findString).split()
    if len(clear_find_string) != 2 or clear_find_string[0] != "find" or clear_find_string[1][0] != "@":
        bot.send_message(chat_id, "Вы неправильно ввели команду")
        return
    find_by_username(chat_id, clear_find_string[1][1:])


def start(chat_id, message_id):
    msg = "Напишите @user, чтобы найти человека в системе"
    bot.tel_send_inlinebutton(chat_id, [], msg, message_id)


def find_by_username(chat_id, username, message_id):
    clear_username_string = str(username).split()
    if len(clear_username_string) != 1:
        bot.send_message(chat_id, "Вы неправильно ввели **username**")
        return
    user = db.get_user_by_username(clear_username_string[0][1:])
    msg = "Пользователь не найден, срочно пригласите его сюда!"
    if len(user) != 0:
        msg = mess_about_user(user)
    bot.tel_send_inlinebutton(chat_id, [], msg)
    if len(user) != 0:
        menu_in_the_end(chat_id, user[0][0], int(message_id)+1)


def menu_in_the_end(chat_id, owner_id, message_id):
    msg = "Возможные действия:"
    buttons = [
        {
            "text": "Посмотреть его файлы",
            "callback_data": f"sfl0_{owner_id}_{message_id}"
        },
        {
            "text": "Вернуться назад",
            "callback_data": f"main_menu_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)

