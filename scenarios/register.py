import database as db
import botCommands as bot
import scenarios.profileMenu as profileMenu
import scenarios.findUser as findUser

def switchFun(callback_query, chat_id):
    str_callback = str(callback_query)
    if str_callback[3] == "0":  # узнали факультет
        ask_direction(chat_id, str_callback)
    elif str_callback[3] == "1":  # узнали направление
        ask_course(chat_id, str_callback)
    elif str_callback[3] == "2":  # узнали курс
        finish(chat_id, str_callback)
    elif str_callback[3] == "9":  # узнали курс
        start(chat_id, None)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def start(chat_id, username):
    if username is not None:
        user = db.get_user_by_username(username)
        if len(user) != 0:
            bot.send_message(chat_id, "вы успешно авторизированны!")
            profileMenu.show_menu(chat_id)
            return
        db.insert_user(chat_id, username)
    msg = "В каком факультете вы обучаетесь?"
    buttons = [
        {
            "text": "IITMM",
            "callback_data": "reg0_IITMM"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_direction(chat_id, faculty):
    db.create_new_session(chat_id, faculty.replace("reg0_", ""))
    msg = "На каком направлении вы обучаетесь?"
    buttons = [
        {
            "text": "FIIT",
            "callback_data": "reg1_FIIT"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_course(chat_id, direction):
    db.update_session(chat_id, direction.replace("reg1", ""))
    msg = "На каком курсе вы обучаетесь?"
    buttons = [
        {
            "text": "1",
            "callback_data": "reg2_1"
        },
        {
            "text": "2",
            "callback_data": "reg2_2"
        },
        {
            "text": "3",
            "callback_data": "reg2_3"
        },
        {
            "text": "4",
            "callback_data": "reg2_4"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def finish(chat_id, course):
    session = db.get_session(chat_id)
    db.delete_session(chat_id)
    if len(session) == 0 or len(session[0]) == 0:
        bot.send_message(chat_id, "error in registration")
        return
    data = session[0][1].split("_")
    if len(data) != 2:
        bot.send_message(chat_id, "error in registration")
        return
    facultyList = ["IITMM"]
    directionList = ["FIIT"]
    db.update_user_data(facultyList.index(data[0]), directionList.index(data[1]), course.replace("reg2_", ""), chat_id)
    msg = "Данные сохранены!\nНажмите /menu для просмотра менюшки"
    bot.send_message(chat_id, msg)
