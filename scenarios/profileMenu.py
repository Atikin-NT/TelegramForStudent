import database as db
import botCommands as bot
import scenarios.findUser as findUser
import scenarios.uploadFile as uploadFile
import scenarios.showFiles as showFiles

facultyList = ["IITMM"]
directionList = ["ФИИТ", "ПМИ"]


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


def switchFun(callback_query, chat_id):
    callback_query = str(callback_query)
    if "prf_setting" in callback_query:
        profile_settings(chat_id, callback_query)
    elif callback_query == "prf_info":
        profile_information(chat_id)
    elif "prf_myFiles" in callback_query:
        profile_MyFiles(chat_id, callback_query)
    elif "prf_newFile" in callback_query:
        profile_newFile(chat_id, callback_query)
    elif "prf_fileListAdmin" in callback_query:
        profile_fileListAdmin(chat_id, callback_query)
    elif "prf_fileList" in callback_query:
        profile_fileList(chat_id, callback_query)
    elif "prf_findUser" in callback_query:
        profile_findUser(chat_id, callback_query)
    elif "prf_findFile_by_Name" in callback_query :
        profile_findFile_by_Name(chat_id, callback_query )
    elif "prf_findFile_by_Fac" in callback_query:
        profile_findFile_by_Fac(chat_id, callback_query)
    elif "prf_findFile" in callback_query:
        profile_findFile(chat_id, callback_query)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def show_menu(chat_id, message_id=None):
    if message_id and isinstance(message_id, str):
        message_id = message_id.split("_")[-1]
    msg = "Меню:"
    buttons = [
        {
            "text": "Настройки",
            "callback_data": f"prf_setting_{message_id}"
        },
        {
            "text": "Информация о приложении",
            "callback_data": "prf_info"
        },
        {
            "text": "Мои файлы",
            "callback_data": f"prf_myFiles_{message_id}"
        },
        {
            "text": "Найти пользователя",
            "callback_data": f"prf_findUser_{message_id}"
        },
        {
            "text": "Найти файл",
            "callback_data": f"prf_findFile_{message_id}"
        }
    ]

    user_info = db.get_user_by_id(chat_id)
    if len(user_info) == 0:
        return
    user_info = user_info[0]
    if user_info[0] == 708133213:
        buttons.append({
            "text": "Админка",
            "callback_data": f"adm0_{message_id}"
        })

    if message_id and isinstance(message_id, str):
        bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)
    else:
        bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_settings(chat_id, callback_query):
    message_id = callback_query.replace("prf_setting_", "")
    user = db.get_user_by_id(chat_id)
    msg = mess_about_user(user)
    buttons = [
        {
            "text": "Изменить",
            "callback_data": "reg9"
        },
        {
            "text": "Вернуться назад",
            "callback_data": f"main_menu_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def profile_information(chat_id):
    msg = """
С помощью этого бота вы можете найти любые файлы при подготовке к контрольным, зачетам и экзаменам.
Бот предоставляет возможность загружать файлы(в данный момент только форматы pdf), искать файлы по названию или своему факультету/направлению/курсу/предмету
Сейчас происходит бетта-тестирование бота, поэтому возможны ошибки и баги.
Все кто хочет помочь в разработке или сообщить об ошибке, прошу написать мне: @AtikinNT
"""
    bot.send_message(chat_id, msg)


def profile_MyFiles(chat_id, message_id):
    message_id = message_id.replace("prf_myFiles_", "")
    msg = "Возможные действия"
    buttons = [
        {
            "text": "Добавить новый файл",
            "callback_data": f"prf_newFile_{message_id}"
        },
        {
            "text": "Посмотреть список моих файлов",
            "callback_data": f"prf_fileList_{message_id}"
        },
        {
            "text": "Вернуться назад",
            "callback_data": f"main_menu_{message_id}"
        }
    ]
    user_info = db.get_user_by_id(chat_id)
    if len(user_info) == 0:
        return
    user_info = user_info[0]
    if user_info[4]:
        buttons.append({
            "text": "Файлы на одобрение",
            "callback_data": f"prf_fileListAdmin_{message_id}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def profile_newFile(chat_id, message_id):
    message_id = message_id.replace("prf_newFile_", "")
    uploadFile.ask_course(chat_id, message_id)


def profile_fileList(chat_id, message_id):
    message_id = message_id.replace("prf_fileList_", "")
    filesList = db.get_files_in_profile_page(chat_id)
    if len(filesList) == 0:
        bot.tel_send_inlinebutton(chat_id, [], "у вас нет файлов(", message_id)
        return
    msg = "Список ваших файлов:"
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
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def profile_findUser(chat_id, message_id):
    message_id = message_id.replace("prf_findUser_", "")
    findUser.start(chat_id, message_id)


def profile_fileListAdmin(chat_id, message_id):
    message_id = message_id.replace("prf_fileListAdmin_", "")
    filesList = db.get_files_waiting_for_admin()
    if len(filesList) == 0:
        bot.tel_send_inlinebutton(chat_id, [], "Файлов на одобрение нет)", message_id)
        return
    msg = "Список файлов на одобрение:"
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
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def profile_findFile(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_", "")
    msg = "Выполнить поиск по"
    buttons = [
        {
            "text": "Названию",
            "callback_data": f"prf_findFile_by_Name_{message_id}"
        },
        {
            "text": "Факультету",
            "callback_data": f"prf_findFile_by_Fac_{message_id}"
        },
        {
            "text": "Назад в меню",
            "callback_data": f"main_menu_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def profile_findFile_by_Name(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_by_Name_", "")
    db.create_new_session(chat_id, "findFileByName")
    bot.tel_send_inlinebutton(chat_id, [], "Введите имя файла или ключевое слово", message_id)


def profile_findFile_by_Fac(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_by_Fac_", "")
    db.create_new_session(chat_id, "findFileByFac_")
    showFiles.ask_faculty(chat_id, message_id)
