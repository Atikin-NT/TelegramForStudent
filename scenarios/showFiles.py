import logging
import aiogram
from aiogram.dispatcher.filters import Text
from aiogram.utils import exceptions
from database import db
from aiogram import types
from utils import FindFile
from create_bot import bot
import math


def mess_about_file(fileData):
    filename = fileData['filename']
    course = fileData['course']
    subject = fileData['subject']
    msg = f"""Имя файла: *{filename}*
Курс: *{course}*
Предмет: *{subject}*"""
    return msg


async def ask_subject(callback: aiogram.types.CallbackQuery,
                      state: aiogram.dispatcher.FSMContext):
    """
    Спрашиваем предмет, по которому вывести предметы

    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    state_data = await state.get_data()

    user = db.get_user_by_id(chat_id)
    if user is None or len(user) == 0:
        logging.error(f"Пользователь не найден в функции ask_subject в showFiles, chat_id={chat_id}")
        return
    user = user[0]

    course = user['course']
    direction = user['direction']
    subjects = db.get_subjects(course, direction)
    if subjects is None:
        logging.error(f"Предметы не найдены в функции ask_subject в showFiles, chat_id={chat_id}")
        return

    max_page = math.ceil(len(subjects) / 8)
    if "page_sub" not in state_data:
        await state.update_data(page_sub=1)
        page = 1
    else:
        page = int(state_data['page_sub'])
        if page <= 0:
            page = 1
            await state.update_data(page_sub=page)
            return
        if page > max_page:
            page = max_page
            await state.update_data(page_sub=page)
            return

    msg = "Какой предмет?"
    buttons = []
    for sub in subjects[8 * (page-1): 8 * page]:
        buttons.append([types.InlineKeyboardButton(text=f"{sub['name']}", callback_data=f"{sub['sub_id']}")])

    buttons.append([
        types.InlineKeyboardButton(text="◀️", callback_data="page_left_sub"),
        types.InlineKeyboardButton(text=f"{page} / {max_page}", callback_data="page_none"),
        types.InlineKeyboardButton(text="▶️", callback_data="page_right_sub"),
    ])
    buttons.append([types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(FindFile.askSubject)


async def show_files_list(callback: aiogram.types.CallbackQuery,
                          state: aiogram.dispatcher.FSMContext):
    """
    Показываем список файлов

    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    await state.update_data(subject=int(callback.data))
    state_data = await state.get_data()

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    user = db.get_user_by_id(chat_id)
    if user is None or len(user) == 0:
        logging.error(f"Пользователь не найден в функции show_files_list в showFiles, chat_id={chat_id}")
        return
    user = user[0]

    course = user['course']
    direction = user['direction']
    if 'subject' not in state_data:
        subject = int(callback.data)
    else:
        subject = state_data['subject']
    filesList = db.get_files_by_faculty(0, course, subject, direction)
    if filesList is None:
        buttons = [
            [types.InlineKeyboardButton(text="Вернуться назад", callback_data="ask_subject")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.edit_message_text(
            chat_id=chat_id,
            reply_markup=keyboard,
            text="Файлов не найдено(",
            message_id=message_id)
        await state.set_state(FindFile.showFile)
        return

    max_page = math.ceil(len(filesList) / 8)
    if "page" not in state_data:
        await state.update_data(page=1)
        page = 1
    else:
        page = int(state_data['page'])
        if page <= 0:
            page = 1
            await state.update_data(page=page)
            return
        if page > max_page:
            page = max_page
            await state.update_data(page=page)
            return

    msg = "Какой файл вы хотите посмотреть?"
    buttons = []
    for file in filesList[8 * (page-1): 8 * page]:
        if file['admin_check'] or user['is_admin']:
            buttons.append([types.InlineKeyboardButton(text=f"{file['filename']}", callback_data=f"{file['file_id']}")])

    buttons.append([
        types.InlineKeyboardButton(text="◀️", callback_data="page_left"),
        types.InlineKeyboardButton(text=f"{page} / {max_page}", callback_data="page_none"),
        types.InlineKeyboardButton(text="▶️", callback_data="page_right"),
    ])
    buttons.append([types.InlineKeyboardButton(text="Вернуться назад", callback_data="ask_subject")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
        await state.set_state(FindFile.showFile)
        await state.update_data(subject=subject)
    except aiogram.utils.exceptions.MessageNotModified:
        await callback.answer()


async def page(callback: aiogram.types.CallbackQuery,
               state: aiogram.dispatcher.FSMContext):
    """
    Изменение пагинации

    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: пересылает на функцию show_files_list
    """
    callback_data = callback.data
    state_data = await state.get_data()
    if callback_data == "page_left":
        callback.data = state_data['subject']
        await state.update_data(page=state_data['page'] - 1)
    elif callback_data == "page_left_sub":
        await state.update_data(page_sub=state_data['page_sub'] - 1)
    elif callback_data == "page_right":
        callback.data = state_data['subject']
        await state.update_data(page=state_data['page'] + 1)
    elif callback_data == "page_right_sub":
        await state.update_data(page_sub=state_data['page_sub'] + 1)
    await callback.answer()
    if callback_data == "page_none":
        return
    if "sub" in callback_data:
        await ask_subject(callback, state)
        return
    await show_files_list(callback, state)


async def show_file_info(callback: aiogram.types.CallbackQuery,
                         state: aiogram.dispatcher.FSMContext):
    """
    Показываем информацию о конкретном файле
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    file_id = int(callback.data)

    user = db.get_user_by_id(chat_id)
    if user is None or len(user) == 0:
        logging.error(f"Пользователь не найден в функции show_file_info в showFiles, chat_id={chat_id}")
        return
    user = user[0]

    file = db.get_files_by_file_id(file_id)
    if file is None or len(file) == 0:
        logging.error(f"Файл не найден в функции show_file_info в showFiles, chat_id={chat_id}")
        return
    file = file[0]

    msg = mess_about_file(file)
    buttons = [
        [types.InlineKeyboardButton(text="Скачать", callback_data="download")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="show_files_list")]
    ]
    if user['is_admin']:
        buttons.append([types.InlineKeyboardButton(text="Удалить", callback_data="delete")])
    if user['is_admin']:
        if file['admin_check']:
            buttons.append([types.InlineKeyboardButton(text="Заблокировать", callback_data="ban")])
        else:
            buttons.append([types.InlineKeyboardButton(text="Одобрить", callback_data="un_bun")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id, parse_mode=types.ParseMode.MARKDOWN)
    await state.set_state(FindFile.currentFile)
    await state.update_data(file_id=file['file_id'])


def register_handle_showFiles(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(ask_subject, state=FindFile.startFindFile)
    dp.register_callback_query_handler(ask_subject, Text(equals="ask_subject"), state=FindFile.showFile)

    dp.register_callback_query_handler(page, Text(startswith="page"), state=FindFile.askSubject)
    dp.register_callback_query_handler(show_files_list, state=FindFile.askSubject)
    dp.register_callback_query_handler(show_files_list, Text(equals="show_files_list"), state=FindFile.currentFile)
    dp.register_callback_query_handler(page, Text(startswith="page"), state=FindFile.showFile)

    dp.register_callback_query_handler(show_file_info, state=FindFile.showFile)
