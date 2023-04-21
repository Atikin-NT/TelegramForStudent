import aiogram
from aiogram.dispatcher.filters import Text
from aiogram import types
from utils import Admin
from create_bot import bot


async def main_menu(callback: aiogram.types.CallbackQuery):
    """
    Вывод меню для админа

    :param callback: объект aiogram.types.CallbackQuery
    :return:
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Меню:"
    buttons = [
        [types.InlineKeyboardButton(text="Рассылка сообщения", callback_data="send_mass_message")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def send_message_for_all_users(callback: aiogram.types.CallbackQuery,
                                     state: aiogram.dispatcher.FSMContext):
    """
    Массовая рассылка по всем пользователям. НЕДОРАБОТАНО!!!
    
    :param callback: объект aiogram.types.CallbackQuery
    :param state: aiogram.dispatcher.FSMContext
    :return: None
    """
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    msg = "Введите текст сообщения:"
    await bot.edit_message_text(chat_id=chat_id, reply_markup=[], text=msg, message_id=message_id)
    await state.set_state(Admin.sendMassiveMessage)


def register_handle_admin(dp: aiogram.Dispatcher):
    dp.register_callback_query_handler(main_menu, Text(equals="admin_menu"))
    dp.register_callback_query_handler(send_message_for_all_users, Text(equals="send_mass_message"))

