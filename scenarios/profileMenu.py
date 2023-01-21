import database as db
import scenarios.findUser as findUser
import scenarios.uploadFile as uploadFile
import scenarios.showFiles as showFiles
from app import bot
from aiogram import types

facultyList = ["IITMM"]
directionList = ["ФИИТ", "ПМИ"]


def mess_about_user(userData):
    username = userData[0][1]
    data = userData[0][2]

    faculty = facultyList[userData[0][4]]
    direction = directionList[userData[0][5]]
    course = userData[0][6]

    msg = f"""Имя пользователя: *{username}*
Дата регистрации: *{data}*
Факультет: *{faculty}*
Направление: *{direction}*
Курс: *{course}*"""
    return msg


async def switchFun(callback_query, chat_id):
    callback_query = str(callback_query)
    if "prf_setting" in callback_query:
        await profile_settings(chat_id, callback_query)
    elif callback_query == "prf_info":
        await profile_information(chat_id)
    elif "prf_myFiles" in callback_query:
        await profile_MyFiles(chat_id, callback_query)
    elif "prf_newFile" in callback_query:
        await profile_newFile(chat_id, callback_query)
    elif "prf_fileListAdmin" in callback_query:
        await profile_fileListAdmin(chat_id, callback_query)
    elif "prf_fileList" in callback_query:
        await profile_fileList(chat_id, callback_query)
    elif "prf_findUser" in callback_query:
        await profile_findUser(chat_id, callback_query)
    elif "prf_findFile_by_Name" in callback_query :
        await profile_findFile_by_Name(chat_id, callback_query )
    elif "prf_findFile_by_Fac" in callback_query:
        await profile_findFile_by_Fac(chat_id, callback_query)
    elif "prf_findFile" in callback_query:
        await profile_findFile(chat_id, callback_query)
    else:
        pass


async def show_menu(chat_id, message_id=None):
    if message_id and isinstance(message_id, str):
        message_id = message_id.split("_")[-1]
    msg = "Меню:"
    buttons = [
        [types.InlineKeyboardButton(text="Настройки", callback_data=f"prf_setting_{message_id}")],
        [types.InlineKeyboardButton(text="Информация о приложении", callback_data="prf_info")],
        [types.InlineKeyboardButton(text="Мои файлы", callback_data=f"prf_myFiles_{message_id}")],
        [types.InlineKeyboardButton(text="Найти пользователя", callback_data=f"prf_findUser_{message_id}")],
        [types.InlineKeyboardButton(text="Найти файл", callback_data=f"prf_findFile_{message_id}")]
    ]

    user_info = db.get_user_by_id(chat_id)
    if len(user_info) == 0:
        return
    user_info = user_info[0]
    if user_info[0] == 708133213:
        buttons.append([types.InlineKeyboardButton(text="Админка", callback_data=f"adm0_{message_id}")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if message_id and isinstance(message_id, str):
        await bot.edit_message_text(text=msg, message_id=message_id, chat_id=chat_id, reply_markup=keyboard)
    else:
        await bot.send_message(text=msg, chat_id=chat_id, reply_markup=keyboard)


async def profile_settings(chat_id, callback_query):
    message_id = int(callback_query.replace("prf_setting_", ""))
    print(message_id)
    user = db.get_user_by_id(chat_id)
    msg = mess_about_user(user)
    buttons = [
        [types.InlineKeyboardButton(text="Изменить", callback_data="reg9")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id, parse_mode=types.ParseMode.MARKDOWN)


async def profile_information(chat_id):
    msg = """
С помощью этого бота вы можете найти любые файлы при подготовке к контрольным, зачетам и экзаменам.
Бот предоставляет возможность загружать файлы(в данный момент только форматы pdf), искать файлы по названию или своему факультету/направлению/курсу/предмету
Сейчас происходит бетта-тестирование бота, поэтому возможны ошибки и баги.
Все кто хочет помочь в разработке или сообщить об ошибке, прошу написать мне: @AtikinNT
"""
    await bot.send_message(chat_id=chat_id, text=msg)


async def profile_MyFiles(chat_id, message_id):
    message_id = message_id.replace("prf_myFiles_", "")
    msg = "Возможные действия"
    buttons = [
        [types.InlineKeyboardButton(text="Добавить новый файл", callback_data=f"prf_newFile_{message_id}")],
        [types.InlineKeyboardButton(text="Посмотреть список моих файлов", callback_data=f"prf_fileList_{message_id}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    user_info = db.get_user_by_id(chat_id)
    if len(user_info) == 0:
        return
    user_info = user_info[0]
    print(user_info)
    if user_info[3]:
        buttons.append([types.InlineKeyboardButton(text="Файлы на одобрение", callback_data=f"prf_fileListAdmin_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_newFile(chat_id, message_id):
    message_id = message_id.replace("prf_newFile_", "")
    await uploadFile.ask_course(chat_id, message_id, bot)


async def profile_fileList(chat_id, message_id):
    message_id = int(message_id.replace("prf_fileList_", ""))
    filesList = db.get_files_in_profile_page(chat_id)
    if len(filesList) == 0:
        await bot.edit_message_text(chat_id=chat_id, text="у вас нет файлов(", message_id=message_id)
        return
    msg = "Список ваших файлов:"
    buttons = []
    for file in filesList:
        buttons.append([types.InlineKeyboardButton(text=f"{file[1]}", callback_data=f"sfl8_{file[0]}_{message_id}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data=f"main_menu_{message_id}")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_findUser(chat_id, message_id):
    message_id = message_id.replace("prf_findUser_", "")
    await findUser.start(chat_id, message_id, bot)


async def profile_fileListAdmin(chat_id, message_id):
    message_id = message_id.replace("prf_fileListAdmin_", "")
    filesList = db.get_files_waiting_for_admin()
    if len(filesList) == 0:
        await bot.edit_message_text(chat_id=chat_id, text="Файлов на одобрение нет)", message_id=message_id)
        return
    msg = "Список файлов на одобрение:"
    buttons = []
    for file in filesList:
        buttons.append([types.InlineKeyboardButton(text=f"{file[1]}", callback_data=f"sfl8_{file[0]}_{message_id}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data=f"main_menu_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_findFile(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_", "")
    msg = "Выполнить поиск по"
    buttons = [
        [types.InlineKeyboardButton(text="Факультету", callback_data=f"prf_findFile_by_Fac_{message_id}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_findFile_by_Name(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_by_Name_", "")
    db.create_new_session(chat_id, "findFileByName")
    await bot.edit_message_text(chat_id=chat_id, text="Введите имя файла или ключевое слово", message_id=message_id)


async def profile_findFile_by_Fac(chat_id, message_id):
    message_id = message_id.replace("prf_findFile_by_Fac_", "")
    db.delete_session(chat_id)
    db.create_new_session(chat_id, "findFileByFac_")
    await showFiles.ask_faculty(chat_id, message_id, bot)
