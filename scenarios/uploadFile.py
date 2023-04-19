import logging
from aiogram.dispatcher.filters import Text
from database import db
import aiogram
from aiogram import types
import yaDisk as ya
from create_bot import bot
from utils import UploadFileState


async def ask_course(callback: aiogram.types.CallbackQuery,
                     state: aiogram.dispatcher.FSMContext):
    """
    Спрашиваем какого курса файл
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Файл какого курса обучения?"
    buttons = [
        [types.InlineKeyboardButton(text="1", callback_data="1")],
        [types.InlineKeyboardButton(text="2", callback_data="2")],
        [types.InlineKeyboardButton(text="3", callback_data="3")],
        [types.InlineKeyboardButton(text="4", callback_data="4")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(UploadFileState.course)


async def ask_subject(callback: aiogram.types.CallbackQuery,
                      state: aiogram.dispatcher.FSMContext):
    """
    Спрашиваем предмет для загружаемого файла
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    course = int(callback.data)
    await state.update_data(course=course)

    user = db.get_user_by_id(chat_id)
    if user is None or len(user) == 0:
        logging.error(f"Пользователь не найден в profile_MyFiles. chat_id={chat_id}")
        return
    user = user[0]

    subjects = db.get_subjects(course, user['direction'])
    if subjects is None:
        logging.error(f"Не найдены предметы по след запросу: course={course}, direction={user['direction']}, "
                      f"chat_id={chat_id}")
        return
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append([types.InlineKeyboardButton(text=f"{sub['name']}", callback_data=f"{sub['sub_id']}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(UploadFileState.subject)


async def upload_msg(callback: aiogram.types.CallbackQuery,
                     state: aiogram.dispatcher.FSMContext):
    """
    Сообщение о том, чтобы пользователь загрузил файл
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await state.update_data(subject=int(callback.data))

    msg = "Отправьте файл. Разрешенные форматы `.pdf`"
    await bot.edit_message_text(chat_id=chat_id, text=msg, message_id=message_id, parse_mode=types.ParseMode.MARKDOWN)
    await state.set_state(UploadFileState.wait_for_file)


async def upload_document(message: aiogram.types.Message,
                          state: aiogram.dispatcher.FSMContext):
    """
    Обработка загрузки файла
    :param message: объект aiogram.types.Message
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = message.chat.id
    message_id = message.message_id
    document = message.document
    data = await state.get_data()

    if document.mime_type != "application/pdf":
        await bot.send_message(chat_id, "Недопустимый формат (пока только pdf). Пришлите файл другого формата.")
        return

    user_info = db.get_user_by_id(chat_id)
    if user_info is None or len(user_info) == 0:
        logging.error(f" Пользователь не найден в upload_document, chat_id={chat_id}")
        return
    user_info = user_info[0]

    fileID = document.file_id
    insert = db.insert_file(document.file_name, chat_id, data['course'], data['subject'], user_info['direction'])
    if insert is not None:
        await state.update_data(file_id=fileID)
        msg = "Файл с таким названием уже существует"
        buttons = [
            # [types.InlineKeyboardButton(text="Изменить название", callback_data="change_name")],
            # [types.InlineKeyboardButton(text="Заменить существующий", callback_data="change_file")],
            [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        await state.set_state(UploadFileState.reloadFile)
        return

    download_path = [
        f"/faculty_{user_info['faculty']}",
        f"/direction_{user_info['direction']}",
        f"/course_{data['course']}",
        f"/sub_{data['subject']}",
        f"/{document.file_name}"
    ]

    await ya.upload_to_yadisk(fileID, download_path, bot)

    msg = "Файл загружен. Как только пройдет проверку, он появится в свободном доступе"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)


def register_handle_uploadFile(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(ask_subject, state=UploadFileState.course)
    dp.register_callback_query_handler(upload_msg, state=UploadFileState.subject)
    dp.register_message_handler(upload_document, state=UploadFileState.wait_for_file, content_types=['document'])
