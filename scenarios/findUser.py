import aiogram

import database as db
from aiogram import types

facultyList = ["IITMM"]
directionList = ["FIIT"]


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


# def switch_fun(findString, chat_id):
#     clear_find_string = str(findString).split()
#     if len(clear_find_string) != 2 or clear_find_string[0] != "find" or clear_find_string[1][0] != "@":
#         bot.send_message(chat_id, "Вы неправильно ввели команду")
#         return
#     find_by_username(chat_id, clear_find_string[1][1:])


async def start(chat_id, message_id, bot: aiogram.Bot):
    msg = "Напишите @user, чтобы найти человека в системе"
    await bot.edit_message_text(chat_id=chat_id, text=msg, message_id=message_id)


async def find_by_username(chat_id, username, message_id, bot: aiogram.Bot):
    clear_username_string = str(username).split()
    if len(clear_username_string) != 1:
        await bot.send_message(chat_id=chat_id, text="Вы неправильно ввели **username**")
        return
    user = db.get_user_by_username(clear_username_string[0][1:])

    msg = "Пользователь не найден, срочно пригласите его сюда!"
    buttons = []
    if len(user) != 0:
        msg = mess_about_user(user)
        owner_id = user[0][0]
        buttons.append([types.InlineKeyboardButton(text="Посмотреть его файлы", callback_data=f"sfl0_{owner_id}_{message_id}")],)
    buttons.append([types.InlineKeyboardButton(text="Главное меню", callback_data=f"main_menu_{message_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.delete_message(chat_id, message_id-1)
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN)


async def menu_in_the_end(chat_id, owner_id, message_id, bot: aiogram.Bot):
    msg = "Возможные действия:"
    buttons = [
        [types.InlineKeyboardButton(text="Посмотреть его файлы", callback_data=f"sfl5_{owner_id}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)

