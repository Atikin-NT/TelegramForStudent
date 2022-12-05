import database as db
import botCommands as bot


def mess_about_file(fileData, admin = False):
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
    elif str_callback[3] == "8":  # информация о файле
        show_file_info(chat_id, str_callback)
    else:
        bot.send_message(chat_id, "неизвестная команда")


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
            "callback_data": f"sfl9_{file[0]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def show_file_info(chat_id, file_id):
    user_is_admin = db.get_user_by_id(chat_id)[0]
    file = db.get_files_by_file_id(file_id.replace("sfl8_", ""))
    msg = mess_about_file(file)
    bot.send_message(chat_id, msg)
    buttons = [
        {
            "text": "Скачать",
            "callback_data": f"fop3_{file[0][0]}"
        },
        {
            "text": "Назад в меню",
            "callback_data": "main_menu"
        }
    ]
    # if chat_id == file[0][2] or user_is_admin[4]:
    #     buttons.append({
    #         "text": "Удалить",
    #         "callback_data": f"fop_2{file[0][0]}"
    #     })
    if user_is_admin[4]:
        if file[0][8]:
            buttons.append({
                {
                    "text": "Заблокировать",
                    "callback_data": f"fop1_{file[0]}"
                }
            })
        else:
            buttons.append({
                {
                    "text": "Одобрить",
                    "callback_data": f"fop0_{file[0]}"
                }
            })
    bot.tel_send_inlinebutton(chat_id, buttons, "Возможные действия")


def show_file_info_for_admin(chat_id, file_id):
    file = db.get_files_by_file_id(file_id.replace("sfl9_", ""))
    msg = mess_about_file(file, True)
    bot.send_message(chat_id, msg)
    buttons = [
        {
            "text": "Скачать",
            "callback_data": f"fop3_{file[0]}"  # TODO: дописать функцию
        },
        {
            "text": "Удалить",
            "callback_data": f"fop_2{file[0]}"  # TODO: дописать функцию
        },
        {
            "text": "Назад в меню",
            "callback_data": "main_menu"
        }
    ]
    # if file[0][8]:
    #     buttons.append({
    #         {
    #             "text": "Заблокировать",
    #             "callback_data": f"fop1_{file[0]}"
    #         }
    #     })
    # else:
    #     buttons.append({
    #         {
    #             "text": "Одобрить",
    #             "callback_data": f"fop0_{file[0]}"
    #         }
    #     })
    bot.tel_send_inlinebutton(chat_id, buttons, "Возможные действия")
