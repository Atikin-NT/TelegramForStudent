import database as db
from aiogram import types


async def switchFun(callback_query, chat_id, bot):
    callback_query = str(callback_query)
    if callback_query[3] == "0":
        await main_menu(chat_id, callback_query, bot)
    elif callback_query[3] == "1":
        await send_message_for_all_users(chat_id, callback_query, bot)
    else:
        pass


async def main_menu(chat_id, callback_query, bot):
    message_id = callback_query.replace("adm0_", "")
    msg = "Меню:"
    buttons = [
        [types.InlineKeyboardButton(text="Рассылка сообщения", callback_data=f"adm1_{message_id}")],
        [types.InlineKeyboardButton(text="Вернуться назад", callback_data=f"main_menu_{message_id}")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def send_message_for_all_users(chat_id, callback_query, bot):
    db.create_new_session(chat_id, "massive_message")
    message_id = callback_query.replace("adm1_", "")
    msg = "Введите текст сообщения:"
    await bot.edit_message_text(chat_id=chat_id, reply_markup=[], text=msg, message_id=message_id)

