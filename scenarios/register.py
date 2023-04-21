import logging
import aiogram
from aiogram.dispatcher.filters import Text
from database import db
import scenarios.profileMenu as profileMenu
from aiogram import types
from utils import *
from create_bot import bot


async def change_user_data(callback: aiogram.types.CallbackQuery,
                           state: aiogram.dispatcher.FSMContext):
    """
    Изменение настроек пользователя, только через callback

    :param state: aiogram.dispatcher.FSMContext
    :param callback: объект aiogram.types.CallbackQuery
    :return: None
    """
    await start(callback.message, state)


async def start(message: aiogram.types.Message,
                state: aiogram.dispatcher.FSMContext):
    """
    Вопрос про направление

    :param message: объект aiogram.types.Message
    :param state: aiogram.dispatcher.FSMContext
    :return:
    """
    chat_id = message.chat.id
    message_id = message.message_id
    username = message.from_user.username

    await bot.delete_message(chat_id, message_id)
    await state.set_state(UserRegisterState.faculty)

    user = db.get_user_by_id(chat_id)
    if user is None:
        db.insert_user(chat_id, username)

    msg = "На каком факультете вы обучаетесь?"
    buttons = [
        [types.InlineKeyboardButton(text="ИИТММ", callback_data="register")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)


async def ask_direction(callback: aiogram.types.CallbackQuery,
                        state: aiogram.dispatcher.FSMContext):
    """
    Спрашиваем направление у пользователя

    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    faculty = 0  # TODO: надо бы таблицы факультетов сделать
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


async def ask_course(callback: aiogram.types.CallbackQuery,
                     state: aiogram.dispatcher.FSMContext):
    """
    Спрашиваем курс, на котором учится наш пользователь

    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    direction = int(callback.data)
    await state.update_data(direction=direction)
    await state.set_state(UserRegisterState.course)

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
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
    """
    Записываем всю полученную информацию в базу данных
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    course = int(callback.data)
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_data = await state.get_data()
    logging.info(f"Add new user, chat_id = {chat_id}")

    db.update_user_data(
        user_data['faculty'],
        user_data['direction'],
        course,
        chat_id)
    msg = "Данные сохранены! Добро пожаловать! ヾ(⌐■_■)ノ♪"
    await callback.answer(text=msg, show_alert=True)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await state.finish()
    await profileMenu.show_menu(callback.message, state)


def register_handle_register(dp: aiogram.Dispatcher):
    dp.register_message_handler(start, commands=['login'])
    dp.register_callback_query_handler(change_user_data, Text(equals="change_user_data"))
    dp.register_callback_query_handler(ask_direction, state=UserRegisterState.faculty)
    dp.register_callback_query_handler(ask_course, state=UserRegisterState.direction)
    dp.register_callback_query_handler(finish, state=UserRegisterState.course)
