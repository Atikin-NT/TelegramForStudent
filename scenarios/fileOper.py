import logging
import aiogram.types
from database import db
import yaDisk as ya
from aiogram import types
from aiogram.dispatcher.filters import Text
from create_bot import bot
from utils import Admin, FindFile


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
    await state.set_state(Admin.deleteFile)


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
    try:
        await bot.delete_message(chat_id, message_id)
        await ya.download_from_yadisk(chat_id, download_path, file['filename'], bot)

        msg = "возможные действия:"
        buttons = [
            [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        db.update_download_counter(data['file_id'])
    except Exception as ex:
        logging.error(f"ошибка в download_file, ex={ex}")


def register_handle_fileOper(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(approve, Text(equals="un_bun"), state=FindFile.currentFile)
    dp.register_callback_query_handler(disapprove, Text(equals="bun"), state=FindFile.currentFile)
    dp.register_callback_query_handler(download_file, Text(equals="download"), state=FindFile.currentFile)
