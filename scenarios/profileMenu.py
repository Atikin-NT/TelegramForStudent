import database as db
import botCommands as bot


def switchFun(callback_query, chat_id):
    if str(callback_query) == "profile_setting":
        pass
    elif str(callback_query) == "profile_uploadFile":
        bot.send_message(chat_id, "Напишите filename <имя вашего файла>")
    elif str(callback_query) == "profile_deleteFile":
        pass


def show_menu(chat_id):
    msg = "Меню:"
    buttons = [
        {
            "text": "Изменить данные профиля",
            "callback_data": "profile_setting"
        },
        {
            "text": "Загрузить файл",
            "callback_data": "profile_uploadFile"
        },
        {
            "text": "Удалить файл",
            "callback_data": "profile_deleteFile"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


# showfl_//user_id//course//sub
def ask_subject(chat_id, callback_query):
    subjects = db.get_subjects()
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append({
            "text": f"{sub[1]}",
            "callback_data": f"{callback_query}_{sub[0]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def show_files_list(chat_id, callback_query):
    parse_callback = callback_query.split("_")
    user_id = parse_callback[1]
    course = parse_callback[2]
    subject = parse_callback[3]
    filesList = db.get_files_by_user(user_id, course, subject)
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        buttons.append({
            "text": f"{file[1]}",
            "callback_data": f"download_{file[2]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)
