import database as db
import botCommands as bot


def mess_about_file(fileData, admin=False):
    filename = fileData[0][1]
    course = fileData[0][6]
    subject = fileData[0][7]
    msg = f"""Имя файла: *{filename}*
Курс: *{course}*
Предмет: *{subject}*"""

    if admin:
        msg += f"""file_id: *{fileData[0][0]}*
owner: *{fileData[0][2]}*
is_private: *{fileData[0][3]}*
cost: *{fileData[0][4]}*
admin_check: *{fileData[0][8]}*"""

    return msg


def switchFun(callback_query, chat_id):
    str_callback = str(callback_query)
    if str_callback[3] == "0":  # узнали user_id
        ask_course(chat_id, str_callback)
    elif str_callback[3] == "1":  # узнали какого курса файлы нам нужны
        ask_subject(chat_id, str_callback)
    elif str_callback[3] == "2":  # узнали предмет
        show_files_list(chat_id, str_callback)
    elif str_callback[3] == "3":  # узнали факультет
        ask_direction(chat_id, str_callback)
    elif str_callback[3] == "4":  # узнаем курс
        ask_course(chat_id, str_callback, True)
    elif str_callback[3] == "5":  # узнали предмет
        ask_subject(chat_id, str_callback, True)
    elif str_callback[3] == "6":  # узнали предмет
        show_files_list(chat_id, str_callback, True)
    elif str_callback[3] == "8":  # информация о файле
        show_file_info(chat_id, str_callback)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def ask_course(chat_id, owner_file_id, findFile=False):
    print(owner_file_id)
    sflId = 1
    if not findFile:
        owner_file_id = owner_file_id.replace("sfl0_", "").split("_")
        db.create_new_session(chat_id, owner_file_id[0])
    else:
        owner_file_id = owner_file_id.replace("sfl4_", "").split("_")
        db.update_session(chat_id, "_" + owner_file_id[0])
        sflId = 5
    message_id = owner_file_id[1]
    msg = "Файлы какого курса обучения?"
    buttons = [
        {
            "text": "1",
            "callback_data": f"sfl{sflId}_1_{message_id}"
        },
        {
            "text": "2",
            "callback_data": f"sfl{sflId}_2_{message_id}"
        },
        {
            "text": "3",
            "callback_data": f"sfl{sflId}_3_{message_id}"
        },
        {
            "text": "4",
            "callback_data": f"sfl{sflId}_4_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def ask_subject(chat_id, course, findFile=False):
    print(course)
    sflId = 2
    if not findFile:
        course = course.replace("sfl1_", "").split("_")
        db.update_session(chat_id, "_" + course[0])
    else:
        course = course.replace("sfl5_", "").split("_")
        db.update_session(chat_id, "_" + course[0])
        sflId = 6
    message_id = course[1]
    subjects = db.get_subjects()
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append({
            "text": f"{sub[1]}",
            "callback_data": f"sfl{sflId}_{sub[0]}_{message_id}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def show_files_list(chat_id, callback_query, findFile=False):
    session = db.get_session(chat_id)
    if len(session) == 0:
        bot.send_message(chat_id, "Error: len(session) == 0")
        return
    db.delete_session(chat_id)
    data = session[0][1].split("_")
    print(data, findFile, len(data))
    if (not findFile and len(data) != 2) or (findFile and len(data) != 4):
        bot.send_message(chat_id, "Error in showFile")
        return
    filesList = []
    if not findFile:
        user_is_admin = db.get_user_by_id(chat_id)[0]
        user_id = data[0]
        course = data[1]
        subject = callback_query.replace("sfl2_", "").split("_")
        filesList = db.get_files_by_user(user_id, course, subject[0])
    else:
        course = data[3]
        subject = callback_query.replace("sfl6_", "").split("_")
        filesList = db.get_files_by_faculty(0, 0, course, subject[0])
    message_id = subject[1]
    if len(filesList) == 0:
        bot.tel_send_inlinebutton(chat_id, [], "Файлов не найдено(", message_id)
        return
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        if file[8] or (user_is_admin[4] and (not findFile)):
            buttons.append({
                "text": f"{file[1]}",
                "callback_data": f"sfl8_{file[0]}_{message_id}"
            })
    buttons.append({
            "text": "Назад в меню",
            "callback_data": f"main_menu_{message_id}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def show_file_info(chat_id, file_id):
    file_id = file_id.replace("sfl8_", "").split("_")
    message_id = file_id[1]
    user_is_admin = db.get_user_by_id(chat_id)[0]
    file = db.get_files_by_file_id(file_id[0])
    msg = mess_about_file(file)
    buttons = [
        {
            "text": "Скачать",
            "callback_data": f"fop3_{file[0][0]}"
        },
        {
            "text": "Назад в меню",
            "callback_data": f"main_menu_{message_id}"
        }
    ]
    if user_is_admin[4]:
        if file[0][8]:
            buttons.append({
                "text": "Заблокировать",
                "callback_data": f"fop1_{file[0][0]}"
            })
        else:
            buttons.append({
                "text": "Одобрить",
                "callback_data": f"fop0_{file[0][0]}"
            })
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def ask_faculty(chat_id, message_id):
    msg = "В каком факультете вы обучаетесь?"
    buttons = [
        {
            "text": "IITMM",
            "callback_data": f"sfl3_IITMM_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def ask_direction(chat_id, faculty):
    faculty = faculty.replace("sfl3_", "").split("_")
    db.update_session(chat_id, faculty[0])
    message_id = faculty[1]
    msg = "На каком направлении вы обучаетесь?"
    buttons = [
        {
            "text": "FIIT",
            "callback_data": f"sfl4_FIIT_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def list_files_by_name(chat_id, name, message_id):
    session = db.get_session(chat_id)
    print("by name ", session, message_id)
    if len(session) == 0:
        bot.send_message(chat_id, "Недопустимое сообщение")
        return
    db.delete_session(chat_id)
    data = session[0][1].split("_")
    if len(data) != 1:
        bot.send_message(chat_id, "Error in showFileByName")
        return
    filesList = db.get_files_by_name(name)
    if len(filesList) == 0:
        bot.send_message(chat_id, "Файлов не найдено(")
        return
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        buttons.append({
            "text": f"{file[1]}",
            "callback_data": f"sfl8_{file[0]}_{message_id}"
        })
    buttons.append({
            "text": "Назад в меню",
            "callback_data": f"main_menu_{message_id}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)
