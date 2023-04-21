import logging
import aiogram.types
from database import db
import scenarios.uploadFile as uploadFile
from create_bot import bot
from aiogram import types
from aiogram.dispatcher.filters import Text
from utils import *


def mess_about_user(userData):
    username = userData['username']
    date = userData['login']

    faculty = userData['faculty']
    direction = userData['direction']
    course = userData['course']

    msg = f"""Имя пользователя: *{username}*
Дата регистрации: *{date}*
Факультет: *{faculty}*
Направление: *{direction}*
Курс: *{course}*"""
    return msg


async def callback_menu(callback: aiogram.types.CallbackQuery,
                        state: aiogram.dispatcher.FSMContext):
    """
    Вызов меню, только через callback
    
    :param state: aiogram.dispatcher.FSMContext
    :param callback: объект aiogram.types.CallbackQuery
    :return: None
    """
    await show_menu(callback.message, state, True)


async def show_menu(message: aiogram.types.Message,
                    state: aiogram.dispatcher.FSMContext,
                    edit=False):
    """
    Показывает главное меню
    
    :param state: объект aiogram.types.CallbackQuery
    :param edit: если True, то заменит предыдущее сообщение на меню. Иначе пришлет новым сообщением
    :param message: объект aiogram.types.Message
    иначе пришлет меню в виде нового сообщения
    :return: None
    """
    await state.finish()

    chat_id = message.chat.id
    message_id = message.message_id
    msg = "Меню:"
    buttons = [
        [types.InlineKeyboardButton(text="Настройки", callback_data="menu_setting")],
        [types.InlineKeyboardButton(text="Информация о приложении", callback_data="menu_info")],
        [types.InlineKeyboardButton(text="Мои файлы", callback_data="menu_myFiles")],
        [types.InlineKeyboardButton(text="Найти файл", callback_data="menu_findFile")]
    ]

    user_info = db.get_user_by_id(chat_id)
    if user_info is None or len(user_info) == 0:
        return

    user_info = user_info[0]
    if user_info[0] == 708133213:
        buttons.append([types.InlineKeyboardButton(text="Админка", callback_data="admin_menu")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if edit:
        await bot.edit_message_text(text=msg, chat_id=chat_id, reply_markup=keyboard, message_id=message_id)
    else:
        await bot.send_message(text=msg, chat_id=chat_id, reply_markup=keyboard)


async def profile_settings(callback: aiogram.types.CallbackQuery):
    """
    Категория Настройки. Изменяет последнее сообщение
    
    :param callback: объект aiogram.types.CallbackQuery
    :return: None
    """
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    user = db.get_user_by_id(chat_id)
    if user is None or len(user) == 0:
        logging.error(f"User not found in profile_settings, user_id = {chat_id}")
        return
    user = user[0]
    msg = mess_about_user(user)
    buttons = [
        [types.InlineKeyboardButton(text="Изменить", callback_data="change_user_data")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(
        chat_id=chat_id,
        reply_markup=keyboard,
        text=msg,
        message_id=message_id,
        parse_mode=types.ParseMode.MARKDOWN)


async def profile_information(callback: aiogram.types.CallbackQuery):
    """
    Краткая информация о нашем боте
    
    :param callback: объект aiogram.types.CallbackQuery
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = """
С помощью этого бота вы можете найти любые файлы при подготовке к контрольным, зачетам и экзаменам.
Бот предоставляет возможность загружать файлы(в данный момент только форматы pdf), искать файлы по названию или своему факультету/направлению/курсу/предмету
Сейчас происходит бетта-тестирование бота, поэтому возможны ошибки и баги.
Все кто хочет помочь в разработке или сообщить об ошибке, прошу написать мне: @AtikinNT
"""
    buttons = [
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_MyFiles(callback: aiogram.types.CallbackQuery):
    """
    Меню связанное с файловыми операциями Добавить новый файл|Посмотреть список моих файлов|Вернуться назад
    Если пользователь админ, то еще появляется кнопка Файлы на одобрение
    
    :param callback: объект aiogram.types.CallbackQuery
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Возможные действия"
    buttons = [
        [types.InlineKeyboardButton(text="Добавить новый файл", callback_data="profile_newFile")],
        [types.InlineKeyboardButton(text="Посмотреть список моих файлов", callback_data="profile_fileList")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
    ]
    user_info = db.get_user_by_id(chat_id)
    if user_info is None or len(user_info) == 0:
        logging.error(f"Пользователь не найден в profile_MyFiles. chat_id={chat_id}")
        return
    user_info = user_info[0]
    if user_info['is_admin']:
        buttons.append([types.InlineKeyboardButton(text="Файлы на одобрение", callback_data="profile_fileListAdmin")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def profile_newFile(callback: aiogram.types.CallbackQuery,
                          state: aiogram.dispatcher.FSMContext):
    """
    Обработка нажатия на кнопку "загрузить файл"
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return:
    """
    await uploadFile.ask_course(callback, state)


async def profile_fileList(callback: aiogram.types.CallbackQuery,
                           state: aiogram.dispatcher.FSMContext):
    """
    Выводит список файлов пользователя
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    filesList = db.get_files_in_profile_page(chat_id)

    if filesList is None or len(filesList) == 0:
        await bot.edit_message_text(chat_id=chat_id, text="у вас нет файлов(", message_id=message_id)
        return

    msg = "Список ваших файлов:"
    buttons = []
    for file in filesList:
        buttons.append([types.InlineKeyboardButton(text=f"{file['filename']}", callback_data=f"{file['file_id']}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data=f"main_menu")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(UserFileList.showFile)


async def profile_fileListAdmin(callback: aiogram.types.CallbackQuery,
                                state: aiogram.dispatcher.FSMContext):
    """
    Вывод файлов на одобрение (минимальная админка)
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    filesList = db.get_files_waiting_for_admin()
    if filesList is None or len(filesList) == 0:
        await callback.answer(text="Файлов на одобрение нет)", show_alert=True)
        return
    msg = "Список файлов на одобрение:"
    buttons = []
    for file in filesList:
        buttons.append([types.InlineKeyboardButton(text=f"{file['filename']}", callback_data=f"{file['file_id']}")])
    buttons.append([types.InlineKeyboardButton(text="Назад в меню", callback_data="main_menu")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(FindFile.showFile)


async def profile_findFile(callback: aiogram.types.CallbackQuery,
                           state: aiogram.dispatcher.FSMContext):
    """
    Подменю по поиску файлов: Предмету|
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Выполнить поиск по"
    buttons = [
        [types.InlineKeyboardButton(text="Предмету", callback_data="find_by_subject")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(FindFile.startFindFile)


def register_handle_profileMenu(dp: aiogram.Dispatcher):
    dp.register_message_handler(show_menu, commands=['menu'], state="*")
    dp.register_callback_query_handler(callback_menu, Text(equals="main_menu"), state="*")
    dp.register_callback_query_handler(profile_settings, Text(equals="menu_setting"))
    dp.register_callback_query_handler(profile_information, Text(equals="menu_info"))
    dp.register_callback_query_handler(profile_MyFiles, Text(equals="menu_myFiles"))
    dp.register_callback_query_handler(profile_newFile, Text(equals="profile_newFile"))
    dp.register_callback_query_handler(profile_fileList, Text(equals="profile_fileList"))
    dp.register_callback_query_handler(profile_fileListAdmin, Text(equals="profile_fileListAdmin"))
    dp.register_callback_query_handler(profile_findFile, Text(equals="menu_findFile"))
