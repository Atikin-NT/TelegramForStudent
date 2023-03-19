from database import db
import aiogram
from aiogram import types


def mess_about_file(fileData, admin=False):
    filename = fileData[0][1]
    course = fileData[0][3]
    subject = fileData[0][4]
    msg = f"""Имя файла: *{filename}*
Курс: *{course}*
Предмет: *{subject}*"""
    print("return")
    return msg


async def switchFun(callback: aiogram.types.CallbackQuery, bot):
    str_callback = str(callback.data)
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    if str_callback[3] == "0":  # узнали user_id
        await ask_course(chat_id, str_callback, message_id, bot)
    elif str_callback[3] == "1":  # узнали какого курса файлы нам нужны
        await ask_subject(chat_id, bot, message_id)
    elif str_callback[3] == "2":  # узнали предмет
        await show_files_list(chat_id, str_callback, message_id, bot)
    elif str_callback[3] == "3":  # узнали факультет
        await ask_direction(chat_id, str_callback, bot)
    elif str_callback[3] == "4":  # узнаем курс
        await ask_course(chat_id, str_callback, message_id, bot, True)
    elif str_callback[3] == "6":  # узнали предмет
        await show_files_list(chat_id, callback, message_id, bot, True)
    elif str_callback[3] == "8":  # информация о файле
        await show_file_info(chat_id, str_callback, bot, message_id)
    else:
        pass


async def ask_course(chat_id, owner_file_id, message_id, bot: aiogram.Bot, findFile=False):
    sflId = 1
    if not findFile:
        owner_file_id = owner_file_id.replace("sfl0_", "").split("_")
        db.delete_session(chat_id)
        db.create_new_session(chat_id, owner_file_id[0])
    else:
        owner_file_id = owner_file_id.replace("sfl4_", "").split("_")
        db.update_session(chat_id, "_" + owner_file_id[0])
        sflId = 5
    msg = "Файлы какого курса обучения?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data=f"sfl{sflId}_1_{message_id}")],
        [types.InlineKeyboardButton(text="2", callback_data=f"sfl{sflId}_2_{message_id}")],
        [types.InlineKeyboardButton(text="3", callback_data=f"sfl{sflId}_3_{message_id}")],
        [types.InlineKeyboardButton(text="4", callback_data=f"sfl{sflId}_4_{message_id}")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def ask_subject(chat_id, bot: aiogram.Bot, message_id):
    user = db.get_user_by_id(chat_id)[0]
    course = user[6]
    direction = user[5]
    subjects = db.get_subjects(course, direction)
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append([types.InlineKeyboardButton(text=f"{sub[1]}", callback_data=f"sfl2_{sub[0]}")])
    buttons.append([types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def show_files_list(chat_id, callback_query, message_id, bot: aiogram.Bot):
    data = callback_query.split("_")
    user = db.get_user_by_id(chat_id)[0]
    direction = user[5]
    course = user[6]
    subject = data[-1]
    filesList = db.get_files_by_faculty(0, course, subject, direction)
    if len(filesList) == 0:
        buttons = [
            [types.InlineKeyboardButton(text="Вернуться назад", callback_data="sfl1")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text="Файлов не найдено(", message_id=message_id)
        return

    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList:
        if file[5] or user[3]:
            buttons.append([types.InlineKeyboardButton(text=f"{file[1]}", callback_data=f"sfl8_{file[0]}")])
    buttons.append([types.InlineKeyboardButton(text="Вернуться назад", callback_data="sfl1")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def show_file_info(chat_id, file_id, bot: aiogram.Bot, message_id):
    file_id = file_id.split("_")[-1]
    user = db.get_user_by_id(chat_id)[0]
    file = db.get_files_by_file_id(file_id)
    msg = mess_about_file(file)
    buttons = [
        [types.InlineKeyboardButton(text="Скачать", callback_data=f"fop3_{file[0][0]}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"sfl2_{file[0][4]}")]
    ]
    if user[0] == file[0][2] or user[3]:
        buttons.append([types.InlineKeyboardButton(text="Удалить", callback_data=f"fop2_{file[0][0]}")])
    if user[3]:
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
