import logging
import random
import aiogram.types
import yaDisk
from database import db
import yaDisk as ya
from aiogram import types
from aiogram.dispatcher.filters import Text
from create_bot import bot, ROOT_DIR
from utils import FindFile, UserFileList
from scenarios.profileMenu import show_menu


async def approve(callback: aiogram.types.CallbackQuery,
                  state: aiogram.dispatcher.FSMContext):
    """
    Функция подтверждения файла (доступна только админам)

    :param callback: объект aiogram.types.CallbackQuery
    :param state: объект aiogram.dispatcher.FSMContext
    :return: None
    """
    data = await state.get_data()
    db.change_file_admin_status(data['file_id'], True)
    await callback.answer(text="Теперь файл в свободном доступе", show_alert=True)


async def disapprove(callback: aiogram.types.CallbackQuery,
                     state: aiogram.dispatcher.FSMContext):
    """
    Функция забанивания файла (доступна только админам)
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: объект aiogram.dispatcher.FSMContext
    :return: None
    """
    data = await state.get_data()
    db.change_file_admin_status(data['file_id'], False)
    await callback.answer(text="Теперь файл закрыт от свободного доступа", show_alert=True)


async def delete_file(callback: aiogram.types.CallbackQuery,
                      state: aiogram.dispatcher.FSMContext):
    """
    Функция удаления файла (доступна только админам)
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: объект aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Вы уверены, что хотите удалить?"
    buttons = [
        [types.InlineKeyboardButton(text="Да", callback_data=callback.data)],
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)
    await state.set_state(UserFileList.deleteFile)


async def delete_file_confirm(callback: aiogram.types.CallbackQuery,
                              state: aiogram.dispatcher.FSMContext):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    state_data = await state.get_data()

    file_id = int(state_data["file_id"])
    file = db.get_files_by_file_id(file_id)
    if file is None:
        logging.error(f"Не удалось удалить файл, file_id={file_id}")
        return
    file = file[0]
    owner = db.get_user_by_id(file['owner'])
    if owner is None:
        logging.error(f"не найден создатель файла, user_id={file['owner']}")
        return
    owner = owner[0]

    file_path = f"/faculty_{owner['faculty']}/direction_{owner['direction']}/course_{file['course']}" \
                f"/sub_{file['subject']}/{file['filename']}"

    if yaDisk.delete_file_from_yadisk(file_path):
        await bot.send_message(chat_id=chat_id, text="Произошла ошибка, пожалуйста напишите сообщение об этом в тех "
                                                     "поддержку")
        return

    db.delete_file_by_file_id(file_id)

    await callback.answer(text="Файл удален", show_alert=True)
    await show_menu(callback.message, state, True)


async def download_file(callback: aiogram.types.CallbackQuery,
                        state: aiogram.dispatcher.FSMContext):
    """
    Скачивание файла
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: объект aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    data = await state.get_data()
    file = db.get_files_by_file_id(data['file_id'])
    if file is None:
        logging.error(f"Пытаемся скачать не существующий файл, file_if={data['file_id']}")
        return
    file = file[0]

    file_owner = db.get_user_by_id(file['owner'])
    if file_owner is None:
        logging.error(f"Владелец файла не найден, file_id={data['file_id']}, chat_id={chat_id}")
        return
    file_owner = file_owner[0]

    download_path = f"/faculty_{file_owner['faculty']}/direction_{file['direction_id']}/course_{file['course']}" \
                    f"/sub_{file['subject']}/{file['filename']}"
    await bot.delete_message(chat_id, message_id)

    animation_id = random.randint(1, 3)
    animation = open(f"{ROOT_DIR}/static/load_file{animation_id}.gif", "rb")
    await bot.send_animation(chat_id=chat_id, animation=animation, caption="Пожалуйста подождите, ваш файл загружается")
    animation.close()

    try:
        await ya.download_from_yadisk(chat_id, download_path, file['filename'], bot)
        await bot.delete_message(chat_id, message_id+1)

        msg = "возможные действия:"
        buttons = [
            [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        db.update_download_counter(data['file_id'])
    except Exception as ex:
        await bot.delete_message(chat_id, message_id + 1)
        await bot.send_message(chat_id=chat_id, text="Произошла ошибка, напишите пожалуйста в тех поддержку")
        logging.error(f"ошибка в download_file, ex={ex}")


def register_handle_fileOper(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(approve, Text(equals="un_bun"), state=FindFile.currentFile)
    dp.register_callback_query_handler(disapprove, Text(equals="bun"), state=FindFile.currentFile)
    dp.register_callback_query_handler(download_file, Text(equals="download"), state=FindFile.currentFile)
    dp.register_callback_query_handler(delete_file, Text(equals="delete"), state=FindFile.currentFile)
    dp.register_callback_query_handler(delete_file_confirm, state=UserFileList.deleteFile)
