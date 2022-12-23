import database as db
import botCommands as bot
import scenarios.profileMenu as profileMenu


def switchFun(callback_query, chat_id, message_id):
    str_callback = str(callback_query)
    if str_callback[3] == "0":  # узнали факультет
        ask_direction(chat_id, str_callback)
    elif str_callback[3] == "1":  # узнали направление
        ask_course(chat_id, str_callback)
    elif str_callback[3] == "2":  # узнали курс
        finish(chat_id, str_callback)
    elif str_callback[3] == "9":  # узнали курс
        start(chat_id, None, message_id)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def start(chat_id, username, message_id):
    if username is not None:
        user = db.get_user_by_id(chat_id)
        if len(user) != 0:
            bot.send_message(chat_id, "вы успешно авторизированны!")
            profileMenu.show_menu(chat_id)
            return
        db.insert_user(chat_id, username)
    msg = "В каком факультете вы обучаетесь?"
    buttons = [
        {
            "text": "IITMM",
            "callback_data": f"reg0_IITMM_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_direction(chat_id, faculty):
    faculty = faculty.replace("reg0_", "").split("_")

    message_id = faculty[1]
    db.create_new_session(chat_id, faculty[0])
    msg = "На каком направлении вы обучаетесь?"
    direction_list = db.get_all_directions()
    buttons = []
    for direction in direction_list:
        buttons.append({
            "text": f"{direction[1]}",
            "callback_data": f"reg1_{direction[0]}_{message_id}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def ask_course(chat_id, direction):
    direction = direction.replace("reg1_", "").split("_")
    message_id = direction[1]
    db.update_session(chat_id, "_" + direction[0])
    msg = "На каком курсе вы обучаетесь?"
    buttons = [
        {
            "text": "1",
            "callback_data": f"reg2_1_{message_id}"
        },
        {
            "text": "2",
            "callback_data": f"reg2_2_{message_id}"
        },
        {
            "text": "3",
            "callback_data": f"reg2_3_{message_id}"
        },
        {
            "text": "4",
            "callback_data": f"reg2_4_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def finish(chat_id, course):
    course = course.replace("reg2_", "").split("_")
    message_id = course[1]
    session = db.get_session(chat_id)
    db.delete_session(chat_id)
    if len(session) == 0 or len(session[0]) == 0:
        bot.send_message(chat_id, "error in registration")
        return
    data = session[0][1].split("_")
    if len(data) != 2:
        bot.send_message(chat_id, "error in registration")
        return
    facultyList = 0
    db.update_user_data(facultyList, data[1], course[0], chat_id)
    msg = "Данные сохранены!\nНажмите /menu для просмотра менюшки"
    bot.tel_send_inlinebutton(chat_id, [], msg, message_id)
