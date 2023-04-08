import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from database import db
import scenarios.profileMenu as profileMenu
from aiogram import types
from utils import *
from create_bot import bot


async def switchFun(callback: aiogram.types.CallbackQuery,
                    bot: aiogram.Bot,
                    state: aiogram.dispatcher.FSMContext):
    str_callback = str(callback.data)
    message_id = callback.message.message_id
    chat_id = callback.from_user.id
    current_state = await state.get_state()

    if current_state is None:
        await state.set_state(UserRegisterState.faculty)
        await ask_direction(chat_id, bot, message_id, state)
    elif str_callback[3] == "1":  # узнали направление
        await ask_course(chat_id, str_callback, bot)
    elif str_callback[3] == "2":  # узнали курс
        await finish(chat_id, str_callback, callback, bot)
    elif str_callback[3] == "9":  # узнали курс
        await start(chat_id, None, message_id, bot)
    else:
        pass


async def start(callback: aiogram.types.CallbackQuery,
                state: aiogram.dispatcher.FSMContext):
    chat_id = callback.message.chat
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)
    await state.set_state(UserRegisterState.faculty)
    # if username is not None:
    #     user = db.get_user_by_id(chat_id)
    #     if len(user) != 0 and user[0][4] != -1 and user[0][5] != -1 and user[0][6] != -1:
    #         await profileMenu.show_menu(chat_id, message_id, False)
    #         return
    #     db.insert_user(chat_id, username)
    msg = "На каком факультете вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="ИИТММ", callback_data="register")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)


async def ask_direction(callback: aiogram.types.CallbackQuery,
                        state: aiogram.dispatcher.FSMContext):
    chat_id = callback.message.chat
    message_id = callback.message.message_id
    faculty = "IITMM"  # TODO: надо бы таблицы факультетов сделать
    await state.update_data(faculty=faculty)
    await state.set_state(UserRegisterState.direction)
    msg = "На каком направлении вы обучаетесь?"
    direction_list = db.get_all_directions()
    buttons = []
    for direction in direction_list:
        buttons.append([types.InlineKeyboardButton(text=f"{direction[1]}", callback_data=f"{direction[0]}")])
        break
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    print("ok")


async def ask_course(callback: aiogram.types.CallbackQuery,
                     state: aiogram.dispatcher.FSMContext):
    direction = int(callback.data)
    await state.update_data(direction=direction)
    await state.set_state(UserRegisterState.course)

    chat_id = callback.message.chat
    message_id = callback.message.message_id
    db.update_session(chat_id, "_" + direction[0])
    msg = "На каком курсе вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data="1")],
        [types.InlineKeyboardButton(text="2", callback_data="2")],
        [types.InlineKeyboardButton(text="3", callback_data="3")],
        [types.InlineKeyboardButton(text="4", callback_data="4")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def finish(callback: aiogram.types.CallbackQuery,
                 state: aiogram.dispatcher.FSMContext):
    course = int(callback.data)
    chat_id = callback.message.chat
    message_id = callback.message.message_id
    user_data = state.get_data()
    print(user_data)


    # facultyList = 0
    # db.update_user_data(facultyList, data[1], course[0], chat_id)
    msg = "Данные сохранены! Добро пожаловать! ヾ(⌐■_■)ノ♪"
    await callback.answer(text=msg, show_alert=True)
    await profileMenu.show_menu(chat_id, message_id, True)


def register_handle_register(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(start, Text(equals="register"))
    dp.register_callback_query_handler(ask_direction, state=UserRegisterState.faculty)
    dp.register_callback_query_handler(ask_course, state=UserRegisterState.direction)
    dp.register_callback_query_handler(finish, state=UserRegisterState.course)
