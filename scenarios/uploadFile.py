import database as db
import aiogram
from aiogram import types
import yaDisk as ya


async def switchFun(callback: aiogram.types.CallbackQuery, bot):
    chat_id = callback.from_user.id
    parse_callback = str(callback.data)
    message_id = callback.message.message_id
    if parse_callback[4] == "0":  # узнали курс
        await ask_subject(chat_id, parse_callback, bot)
    elif parse_callback[4] == "1":  # узнали предмет
        await upload_msg(chat_id, parse_callback, bot)
    elif parse_callback[4] == "2":  # меняем название ,после неудачной загрузки
        await rename_file(chat_id, message_id, bot)
    elif parse_callback[4] == "3":  # обновляем старый файл
        await update_file(chat_id, message_id, bot)
    else:
        pass


async def ask_course(chat_id, message_id, bot: aiogram.Bot):
    msg = "Файл какого курса обучения?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data=f"upld0_1_{message_id}")],
        [types.InlineKeyboardButton(text="2", callback_data=f"upld0_2_{message_id}")],
        [types.InlineKeyboardButton(text="3", callback_data=f"upld0_3_{message_id}")],
        [types.InlineKeyboardButton(text="4", callback_data=f"upld0_4_{message_id}")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def ask_subject(chat_id, course, bot: aiogram.Bot):
    course = course.replace("upld0_", "").split("_")
    message_id = int(course[1])
    db.delete_session(chat_id)
    db.create_new_session(chat_id, course[0])
    user = db.get_user_by_id(chat_id)[0]
    print(user)
    subjects = db.get_subjects(user[6], user[5])
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append([types.InlineKeyboardButton(text=f"{sub[1]}", callback_data=f"upld1_{sub[0]}_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def upload_msg(chat_id, subject, bot: aiogram.Bot):
    subject = subject.replace("upld1_", "").split("_")
    db.update_session(chat_id, "|" + subject[0])
    await bot.edit_message_text(chat_id=chat_id, text="Отправьте файл", message_id=int(subject[1]))


async def upload_document(document :aiogram.types.Document, chat_id, message_id, bot: aiogram.Bot):
    session = db.get_session(chat_id)  # [(708133213, '2_1')]
    await bot.delete_message(chat_id, message_id-1)
    if len(session) == 0 or len(session[0]) == 0:
        await bot.send_message(chat_id, "Ошибка в загрузке файла")
        return

    user_info = db.get_user_by_id(chat_id)[0]  # [(708133213, 'AtikinNT', datetime.date(2022, 11, 21), 0, False, [0, 0, 0, 0, 0], 0, 0, 0, 2)]
    data = session[0][1].split("|")  # [2(course), 1(subject)]
    download_path = [
        f"/faculty_{user_info[4]}",
        f"/direction_{user_info[5]}",
        f"/course_{data[0]}",
        f"/sub_{data[1]}",
        f"/{document['file_name']}",
    ]

    print(document)
    if document["mime_type"] != "application/pdf":
        await bot.send_message(chat_id, "Недопустимый формат (пока только pdf)")
        return
    fileID = document["file_id"]
    insert = db.insert_file(document["file_name"], chat_id, data[0], data[1], user_info[5])
    if insert != -1:
        db.update_session(chat_id, f"|{document.file_id}|{insert}")
        msg = "Файл с таким названием уже существует"
        buttons = [
            [types.InlineKeyboardButton(text="Изменить название", callback_data="upld2")],
            [types.InlineKeyboardButton(text="Заменить существующий", callback_data="upld3")],
            [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu_upld")],
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        return

    await ya.upload_to_yadisk(fileID, download_path, bot)

    await bot.delete_message(chat_id, message_id)
    msg = "Файл загружен. Как только пройдет проверку, он появится в сободном доступе"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)


async def rename_file(chat_id, message_id, bot):
    msg = "Введите новое название файла"
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg)


async def rename_file_new_name(chat_id, message_id, new_filename, bot):
    session = db.get_session(chat_id)[0]
    user_info = db.get_user_by_id(chat_id)[0]
    data = session[1].split("|")
    insert = db.insert_file(new_filename, chat_id, data[0], data[1], user_info[5])
    if insert != -1:
        msg = "Файл с таким названием уже существует"
        buttons = [
            [types.InlineKeyboardButton(text="Изменить название", callback_data="upld2")],
            [types.InlineKeyboardButton(text="Заменить существующий", callback_data="upld3")],
            [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu_upld")],
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        return

    fileID = data[2]
    download_path = [
        f"/faculty_{user_info[4]}",
        f"/direction_{user_info[5]}",
        f"/course_{data[0]}",
        f"/sub_{data[1]}",
        f"/{new_filename}.pdf",
    ]
    await ya.upload_to_yadisk(fileID, download_path, bot)

    await bot.delete_message(chat_id, message_id)
    msg = "Файл загружен. Как только пройдет проверку, он появится в сободном доступе"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
    db.delete_session(chat_id)


async def update_file(chat_id, message_id, bot: aiogram.Bot):
    session = db.get_session(chat_id)  # [(708133213, '2_1_{file_id}')]
    if len(session) == 0 or len(session[0]) == 0:
        await bot.send_message(chat_id, "Ошибка в загрузке файла")
    user_info = db.get_user_by_id(chat_id)[0]  # [(708133213, 'AtikinNT', datetime.date(2022, 11, 21), 0, False, [0, 0, 0, 0, 0], 0, 0, 0, 2)]
    data = session[0][1].split("|")  # [2(course), 1(subject), (file_id_in_tg), (file_id_in_database)]
    document = db.get_files_by_file_id(data[3])[0]
    download_path = [
        f"/faculty_{user_info[4]}",
        f"/direction_{user_info[5]}",
        f"/course_{data[0]}",
        f"/sub_{data[1]}",
        f"/{document[1]}",
    ]

    print(document)
    fileID = data[2]
    await ya.upload_to_yadisk(fileID, download_path, bot)

    await bot.delete_message(chat_id, message_id)

    db.change_file_admin_status(document[0], False)
    msg = "Файл обновлен. Как только пройдет проверку, он появится в сободном доступе"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
