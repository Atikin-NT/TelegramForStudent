import aiogram
import json
from aiogram.dispatcher.filters import Text
from aiogram import types
from utils import Admin
from create_bot import bot
from scenarios.profileMenu import show_menu

with open('env.json', 'r') as file:
    config = json.load(file)
DEV_CHAT_ID = config["DEV_CHAT_ID"]


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


async def feedback(message: aiogram.types.Message,
                   state: aiogram.dispatcher.FSMContext):
    """
    Получение сообщения от пользователя и пересылка его в чат разработчиков
    :param message: объект aiogram.types.Message
    :param state: объект aiogram.types.CallbackQuery
    :return: None
    """
    chat_id = message.chat.id
    message_id = message.message_id

    feedback_msg = message.text
    feedback_username = message.from_user.username
    feedback_time = message.date

    feedback_to_chat = f"Поступил *feedback*\n\n" \
                       f"*От пользователя*: @{feedback_username}\n\n" \
                       f"*Дата*: {feedback_time}"

    await bot.send_message(chat_id=DEV_CHAT_ID,
                           text=feedback_to_chat,
                           parse_mode=types.ParseMode.MARKDOWN)

    await bot.forward_message(chat_id=DEV_CHAT_ID,
                              from_chat_id=chat_id,
                              message_id=message_id)

    msg = "Спасибо за обратную связь)"
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)
    await bot.send_message(chat_id=chat_id, text=msg)
    await show_menu(message, state, False)

    print(feedback_msg, feedback_username, feedback_time)


def register_handle_admin(dp: aiogram.Dispatcher):
    dp.register_message_handler(feedback, state=Admin.feedback)
    dp.register_callback_query_handler(main_menu, Text(equals="admin_menu"))
    dp.register_callback_query_handler(send_message_for_all_users, Text(equals="send_mass_message"))

