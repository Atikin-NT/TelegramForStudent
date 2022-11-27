import database as db
import botCommands as bot


def mess_about_file(fileData):
    filename = fileData[0][1]
    course = fileData[0][7]
    subject = fileData[0][8]
    msg = f"""Имя файла: *{filename}*
Курс: *{course}*
Предмет: *{subject}*"""
    return msg


def switchFun(callback_query, chat_id):
    str_callback = str(callback_query)
    if str_callback[3] == "0":  # узнали user_id
        ask_course(chat_id, str_callback)
    elif str_callback[3] == "1":  # узнали какого курса файлы нам нужны
        ask_subject(chat_id, str_callback)
    elif str_callback[3] == "2":  # узнали предмет
        show_files_list(chat_id, str_callback)
    elif str_callback[3] == "9":  # информация о файле
        show_file_info(chat_id, str_callback)


def ask_course(chat_id, owner_file_id):
    db.create_new_session(chat_id, owner_file_id.replace("sfl0_", ""))
    msg = "Файлы какого курса обучения?"
    buttons = [
        {
            "text": "1",
            "callback_data": "sfl1_1"
        },
        {
            "text": "2",
            "callback_data": "sfl1_2"
        },
        {
            "text": "3",
            "callback_data": "sfl1_3"
        },
        {
            "text": "4",
            "callback_data": "sfl1_4"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_subject(chat_id, course):
    db.update_session(chat_id, course.replace("sfl1", ""))
    subjects = db.get_subjects()
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append({
            "text": f"{sub[1]}",
            "callback_data": f"sfl2_{sub[0]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def show_files_list(chat_id, callback_query):
    session = db.get_session(chat_id)
    if len(session) == 0:
        bot.send_message(chat_id, "len(session) == 0")
        return
    db.delete_session(chat_id)
    data = session[0][1].split("_")
    if len(data) != 2:
        bot.send_message(chat_id, "error in showFile")
        return

    user_id = data[0]
    course = data[1]
    subject = callback_query.replace("sfl2_", "")
    filesList = db.get_files_by_user(user_id, course, subject)
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        buttons.append({
            "text": f"{file[1]}",
            "callback_data": f"download_{file[2]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def show_file_info(chat_id, file_id):
    print(file_id)
    file = db.get_files_by_file_id(file_id.replace("sfl9_", ""))
    msg = mess_about_file(file)
    bot.send_message(chat_id, msg)
    buttons = [
        {
            "text": "Изменить",
            "callback_data": "reg9"
        },
        {
            "text": "Удалить",
            "callback_data": "main_menu"
        },
        {
            "text": "Вернуться назад",
            "callback_data": "main_menu"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, "Возможные действия")
