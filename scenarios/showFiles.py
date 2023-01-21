import database as db
import aiogram
from aiogram import types


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


async def switchFun(callback_query, chat_id, bot):
    str_callback = str(callback_query)
    if str_callback[3] == "0":  # узнали user_id
        await ask_course(chat_id, str_callback, bot)
    elif str_callback[3] == "1":  # узнали какого курса файлы нам нужны
        await ask_subject(chat_id, str_callback, bot)
    elif str_callback[3] == "2":  # узнали предмет
        await show_files_list(chat_id, str_callback, bot)
    elif str_callback[3] == "3":  # узнали факультет
        await ask_direction(chat_id, str_callback, bot)
    elif str_callback[3] == "4":  # узнаем курс
        await ask_course(chat_id, str_callback, bot, True)
    elif str_callback[3] == "5":  # узнали предмет
        await ask_subject(chat_id, str_callback, bot, True)
    elif str_callback[3] == "6":  # узнали предмет
        await show_files_list(chat_id, str_callback, bot, True)
    elif str_callback[3] == "8":  # информация о файле
        await show_file_info(chat_id, str_callback, bot)
    else:
        pass


async def ask_course(chat_id, owner_file_id, bot: aiogram.Bot, findFile=False):
    sflId = 1
    if not findFile:
        owner_file_id = owner_file_id.replace("sfl0_", "").split("_")
        db.delete_session(chat_id)
        db.create_new_session(chat_id, owner_file_id[0])
    else:
        owner_file_id = owner_file_id.replace("sfl4_", "").split("_")
        db.update_session(chat_id, "_" + owner_file_id[0])
        sflId = 5
    message_id = int(owner_file_id[1])
    msg = "Файлы какого курса обучения?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data=f"sfl{sflId}_1_{message_id}")],
        [types.InlineKeyboardButton(text="2", callback_data=f"sfl{sflId}_2_{message_id}")],
        [types.InlineKeyboardButton(text="3", callback_data=f"sfl{sflId}_3_{message_id}")],
        [types.InlineKeyboardButton(text="4", callback_data=f"sfl{sflId}_4_{message_id}")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def ask_subject(chat_id, course, bot: aiogram.Bot, findFile=False):
    sflId = 2
    session = db.get_session(chat_id)[0][1]
    direction = 0
    if findFile:
        direction = session.split("_")[-1]
    else:
        user = db.get_user_by_id(session)[0]
        direction = user[5]
    if not findFile:
        course = course.replace("sfl1_", "").split("_")
        db.update_session(chat_id, "_" + course[0])
    else:
        course = course.replace("sfl5_", "").split("_")
        db.update_session(chat_id, "_" + course[0])
        sflId = 6
    message_id = int(course[1])
    subjects = db.get_subjects(course[0], direction)
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append([types.InlineKeyboardButton(text=f"{sub[1]}", callback_data=f"sfl{sflId}_{sub[0]}_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def show_files_list(chat_id, callback_query, bot: aiogram.Bot, findFile=False):
    session = db.get_session(chat_id)
    if len(session) == 0:
        await bot.send_message(chat_id, "Error: len(session) == 0")
        return
    db.delete_session(chat_id)
    data = session[0][1].split("_")
    if (not findFile and len(data) != 2) or (findFile and len(data) != 4):
        await bot.send_message(chat_id, "Error in showFile")
        return
    filesList = []
    if not findFile:
        user_is_admin = db.get_user_by_id(chat_id)[0]
        user_id = data[0]
        course = data[1]
        subject = callback_query.replace("sfl2_", "").split("_")
        filesList = db.get_files_by_user(user_id, course, subject[0])
    else:
        direction = data[2]
        course = data[3]
        subject = callback_query.replace("sfl6_", "").split("_")
        filesList = db.get_files_by_faculty(0, direction, course, subject[0])
    message_id = int(subject[1])
    if len(filesList) == 0:
        await bot.edit_message_text(chat_id=chat_id, text="Файлов не найдено(", message_id=message_id)
        return
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        if file[5] or ((not findFile) and user_is_admin[3]):
            buttons.append([types.InlineKeyboardButton(text=f"{file[1]}", callback_data=f"sfl8_{file[0]}_{message_id}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data=f"main_menu_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def show_file_info(chat_id, file_id, bot: aiogram.Bot):
    file_id = file_id.replace("sfl8_", "").split("_")
    message_id = int(file_id[1])
    user_is_admin = db.get_user_by_id(chat_id)[0]
    file = db.get_files_by_file_id(file_id[0])
    msg = mess_about_file(file)
    buttons = [
        [types.InlineKeyboardButton(text="Скачать", callback_data=f"fop3_{file[0][0]}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    if user_is_admin[3]:
        if file[0][5]:
            buttons.append([types.InlineKeyboardButton(text="Заблокировать", callback_data=f"fop1_{file[0][0]}")])
        else:
            buttons.append([types.InlineKeyboardButton(text="Одобрить", callback_data=f"fop0_{file[0][0]}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id, parse_mode=types.ParseMode.MARKDOWN)


async def ask_faculty(chat_id, message_id, bot: aiogram.Bot):
    msg = "В каком факультете вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="IITMM", callback_data=f"sfl3_IITMM_{message_id}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def ask_direction(chat_id, faculty, bot: aiogram.Bot):
    faculty = faculty.replace("sfl3_", "").split("_")
    db.update_session(chat_id, faculty[0])
    message_id = int(faculty[1])
    msg = "На каком направлении вы обучаетесь?"
    direction_list = db.get_all_directions()
    buttons = []
    for direction in direction_list:
        buttons.append([types.InlineKeyboardButton(text=f"{direction[1]}", callback_data=f"sfl4_{direction[0]}_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def list_files_by_name(chat_id, name, message_id, bot: aiogram.Bot):
    session = db.get_session(chat_id)
    if len(session) == 0:
        await bot.send_message(chat_id, "Я не понимаю, чего вы хотите 😞")
        return
    db.delete_session(chat_id)
    data = session[0][1].split("_")
    if len(data) != 1:
        await bot.send_message(chat_id, "Произошла ошибка. Попробуйте заново")
        return
    name = "".join(c for c in name if c.isalnum())
    if len(name) < 2:
        await bot.send_message(chat_id, "Недопустимое сообщние для поиска. Сообщение не может быть слишком коротким или не включать буквы с цифрами")
        return
    filesList = db.get_files_by_name(name)
    if len(filesList) == 0:
        await bot.send_message(chat_id, "Файлов не найдено(")
        return
    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        buttons.append([types.InlineKeyboardButton(text=f"{file[1]}", callback_data=f"sfl8_{file[0]}_{message_id}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data=f"main_menu_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
