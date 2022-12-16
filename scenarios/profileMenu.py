import database as db
import botCommands as bot
import scenarios.findUser as findUser
import scenarios.uploadFile as uploadFile
import scenarios.showFiles as showFiles

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


def switchFun(callback_query, chat_id):
    if str(callback_query) == "prf_setting":
        profile_settings(chat_id)
    elif str(callback_query) == "prf_info":
        profile_information(chat_id)
    elif str(callback_query) == "prf_myFiles":
        profile_MyFiles(chat_id)
    elif str(callback_query) == "prf_newFile":
        profile_newFile(chat_id)
    elif str(callback_query) == "prf_fileList":
        profile_fileList(chat_id)
    elif str(callback_query) == "prf_findUser":
        profile_findUser(chat_id)
    elif str(callback_query) == "prf_fileListAdmin":
        profile_fileListAdmin(chat_id)
    elif str(callback_query) == "prf_findFile":
        profile_findFile(chat_id)
    elif str(callback_query) == "prf_findFile_by_Name":
        profile_findFile_by_Name(chat_id)
    elif str(callback_query) == "prf_findFile_by_Fac":
        profile_findFile_by_Fac(chat_id)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def show_menu(chat_id):
    msg = "Меню:"
    buttons = [
        {
            "text": "Настройки",
            "callback_data": "prf_setting"
        },
        {
            "text": "Информация о приложении",
            "callback_data": "prf_info"
        },
        {
            "text": "Мои файлы",
            "callback_data": "prf_myFiles"
        },
        {
            "text": "Найти пользователя",
            "callback_data": "prf_findUser"
        },
        {
            "text": "Найти файл",
            "callback_data": "prf_findFile"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_settings(chat_id):
    user = db.get_user_by_id(chat_id)
    msg = mess_about_user(user)
    bot.send_message(chat_id, msg)
    buttons = [
        {
            "text": "Изменить",
            "callback_data": "reg9"
        },
        {
            "text": "Вернуться назад",
            "callback_data": "main_menu"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, "Возможные действия")


def profile_information(chat_id):
    msg = """
С помощью этого бота вы можете найти любые файлы при подготовке в контрольным, зачетам и экзаменам.
Бот предоставляет возможность загружать файлы(в данный момент только форматы pdf), искать файлы по названию или своему факультету/направлению/курсу/предмету
Сейчас происходит бетта-тестирование бота, поэтому возможны ошибки и баги.
Все кто хочет помочь в разработке или сообщить об ошибке, прошу написать мне: @AtikinNT
"""
    bot.send_message(chat_id, msg)


def profile_MyFiles(chat_id):
    msg = "Возможные действия"
    buttons = [
        {
            "text": "Добавить новый файл",
            "callback_data": "prf_newFile"
        },
        {
            "text": "Посмотреть список моих файлов",
            "callback_data": "prf_fileList"
        },
        {
            "text": "Вернуться назад",
            "callback_data": "main_menu"
        }
    ]
    user_info = db.get_user_by_id(chat_id)[0]
    if user_info[4]:
        buttons.append({
            "text": "Файлы на одобрение",
            "callback_data": "prf_fileListAdmin"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_newFile(chat_id):
    uploadFile.ask_course(chat_id)


def profile_fileList(chat_id):
    filesList = db.get_files_in_profile_page(chat_id)
    if len(filesList) == 0:
        bot.send_message(chat_id, "у вас нет файлов(")
        return
    msg = "Список ваших файлов:"
    buttons = []
    for file in filesList:
        buttons.append({
            "text": f"{file[1]}",
            "callback_data": f"sfl8_{file[0]}"
        })
    buttons.append({
        "text": "Назад в меню",
        "callback_data": "main_menu"
    })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_findUser(chat_id):
    findUser.start(chat_id)


def profile_fileListAdmin(chat_id):
    filesList = db.get_files_waiting_for_admin()
    if len(filesList) == 0:
        bot.send_message(chat_id, "Файлов на одобрение нет)")
        return
    msg = "Список файлов на одобрение:"
    buttons = []
    for file in filesList:
        buttons.append({
            "text": f"{file[1]}",
            "callback_data": f"sfl8_{file[0]}"
        })
    buttons.append({
            "text": "Назад в меню",
            "callback_data": "main_menu"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_findFile(chat_id):
    msg = "Выполнить поиск по"
    buttons = [
        {
            "text": "Названию",
            "callback_data": "prf_findFile_by_Name"
        },
        {
            "text": "Факультету",
            "callback_data": "prf_findFile_by_Fac"
        },
        {
            "text": "Назад в меню",
            "callback_data": "main_menu"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def profile_findFile_by_Name(chat_id):
    db.create_new_session(chat_id, "findFileByName")
    bot.send_message(chat_id, "Введите имя файла или ключевое слово")


def profile_findFile_by_Fac(chat_id):
    db.create_new_session(chat_id, "findFileByFac_")
    showFiles.ask_faculty(chat_id)
