import database as db
import aiogram
from aiogram import types
import botCommands as ya


async def switchFun(callback_query, chat_id, bot):
    parse_callback = str(callback_query)
    if parse_callback[4] == "0":  # узнали курс
        await ask_subject(chat_id, parse_callback, bot)
    elif parse_callback[4] == "1":  # узнали предмет
        await upload_msg(chat_id, parse_callback, bot)
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
    db.update_session(chat_id, "_" + subject[0])
    await bot.edit_message_text(chat_id=chat_id, text="Отправьте файл", message_id=int(subject[1]))


# Факультет/напрвление/курс/предмет
async def upload_document(document, chat_id, message_id, bot: aiogram.Bot):
    session = db.get_session(chat_id)  # [(708133213, '2_1')]
    db.delete_session(chat_id)
    await bot.delete_message(chat_id, message_id-1)
    if len(session) == 0 or len(session[0]) == 0:
        await bot.send_message(chat_id, "Ошибка в загрузке файла")
        return

    user_info = db.get_user_by_id(chat_id)[0]  # [(708133213, 'AtikinNT', datetime.date(2022, 11, 21), 0, False, [0, 0, 0, 0, 0], 0, 0, 0, 2)]
    data = session[0][1].split("_")  # [2(course), 1(subject)]
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
    db.insert_file(document["file_name"], chat_id, data[0], data[1], user_info[5])
    await ya.upload_to_yadisk(fileID, download_path, bot)

    await bot.delete_message(chat_id, message_id)
    msg = "Файл загружен. Как только пройдет проверку, он появится в сободном доступе"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
