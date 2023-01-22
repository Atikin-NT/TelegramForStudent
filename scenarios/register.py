import aiogram
import database as db
import scenarios.profileMenu as profileMenu
from aiogram import types


async def switchFun(callback: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    str_callback = str(callback.data)
    message_id = callback.message.message_id
    chat_id = callback.from_user.id
    if str_callback[3] == "0":  # узнали факультет
        await ask_direction(chat_id, str_callback, bot)
    elif str_callback[3] == "1":  # узнали направление
        await ask_course(chat_id, str_callback, bot)
    elif str_callback[3] == "2":  # узнали курс
        await finish(chat_id, str_callback, callback, bot)
    elif str_callback[3] == "9":  # узнали курс
        await start(chat_id, None, message_id, bot)
    else:
        pass


async def start(chat_id, username, message_id, bot):
    await bot.delete_message(chat_id, message_id)
    if username is not None:
        user = db.get_user_by_id(chat_id)
        if len(user) != 0 and user[0][4] != -1 and user[0][5] != -1 and user[0][6] != -1:
            await profileMenu.show_menu(chat_id, message_id, False)
            return
        db.insert_user(chat_id, username)
    msg = "В каком факультете вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="ИИТММ", callback_data=f"reg0_IITMM_{message_id+1}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)


async def ask_direction(chat_id, faculty, bot):
    faculty = faculty.replace("reg0_", "").split("_")

    message_id = int(faculty[1])
    db.delete_session(chat_id)
    db.create_new_session(chat_id, faculty[0])
    msg = "На каком направлении вы обучаетесь?"
    direction_list = db.get_all_directions()
    buttons = []
    for direction in direction_list:
        buttons.append([types.InlineKeyboardButton(text=f"{direction[1]}", callback_data=f"reg1_{direction[0]}_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def ask_course(chat_id, direction, bot):
    direction = direction.replace("reg1_", "").split("_")
    message_id = int(direction[1])
    db.update_session(chat_id, "_" + direction[0])
    msg = "На каком курсе вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data=f"reg2_1_{message_id}")],
        [types.InlineKeyboardButton(text="2", callback_data=f"reg2_2_{message_id}")],
        [types.InlineKeyboardButton(text="3", callback_data=f"reg2_3_{message_id}")],
        [types.InlineKeyboardButton(text="4", callback_data=f"reg2_4_{message_id}")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def finish(chat_id, course, callback, bot):
    course = course.replace("reg2_", "").split("_")
    message_id = int(course[1])
    session = db.get_session(chat_id)
    db.delete_session(chat_id)
    if len(session) == 0 or len(session[0]) == 0:
        await bot.send_message(chat_id=chat_id, text="error in registration")
        return
    data = session[0][1].split("_")
    if len(data) != 2:
        await bot.send_message(chat_id=chat_id, text="error in registration")
        return
    facultyList = 0
    db.update_user_data(facultyList, data[1], course[0], chat_id)
    msg = "Данные сохранены! Добро пожаловать! ヾ(⌐■_■)ノ♪"
    await callback.answer(text=msg, show_alert=True)
    await profileMenu.show_menu(chat_id, message_id, True)
