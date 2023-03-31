import aiogram.types
from database import db
import yaDisk as ya
from aiogram import types


async def switchFun(callback_query: aiogram.types.CallbackQuery, bot: aiogram.Bot):
    parse_callback = str(callback_query.data)
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    if parse_callback[3] == "0":  # одобрили
        await approve(parse_callback, callback_query)
    elif parse_callback[3] == "1":  # заблокировали
        await disapprove(parse_callback, callback_query)
    elif parse_callback[3] == "2":  # удалить файл
        await delete_file(chat_id, parse_callback, bot, message_id)
    elif parse_callback[3] == "3":  # скачать файл
        await download_file(chat_id, parse_callback, bot, message_id)
    elif parse_callback[3] == "4":  # скачать файл
        await delete_file_approve(chat_id, parse_callback, bot, message_id)
    else:
        pass


async def approve(parse_callback, callback_query: aiogram.types.CallbackQuery):
    file_id = parse_callback.replace("fop0_", "")
    db.change_file_admin_status(file_id, True)
    await callback_query.answer(text="Теперь файл в свободном доступе", show_alert=True)


async def disapprove(parse_callback, callback_query: aiogram.types.CallbackQuery):
    file_id = parse_callback.replace("fop1_", "")
    db.change_file_admin_status(file_id, False)
    await callback_query.answer(text="Теперь файл закрыт от свободного доступа", show_alert=True)


async def delete_file(chat_id, parse_callback, bot, message_id):
    callback = parse_callback.replace("fop2", "fop4")
    msg = "Вы уверены, что хотите удалить?"
    buttons = [
        [types.InlineKeyboardButton(text="Да", callback_data=callback)],
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def delete_file_approve(chat_id, parse_callback, bot, message_id):
    file_id_in_db = parse_callback.split("_")[-1]
    file = db.get_files_by_file_id(file_id_in_db)[0]
    user = db.get_user_by_id(chat_id)[0]
    file_path = f"/faculty_{user[4]}/direction_{file[7]}/course_{file[3]}/sub_{file[4]}/{file[1]}.pdf"
    ya.delete_file_from_yadisk(file_path)
    db.delete_file_by_file_id(file_id_in_db)

    msg = "Файл удален"
    buttons = [
        [types.InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.edit_message_text(chat_id=chat_id, reply_markup=keyboard, text=msg, message_id=message_id)


async def download_file(chat_id, parse_callback, bot, message_id):
    file = db.get_files_by_file_id(parse_callback.replace("fop3_", ""))[0]
    file_owner = db.get_user_by_id(file[2])[0]
    download_path = f"/faculty_{file_owner[4]}/direction_{file[7]}/course_{file[3]}/sub_{file[4]}/{file[1]}"
    try:
        await bot.delete_message(chat_id, message_id)
        await ya.download_from_yadisk(chat_id, download_path, file[1], bot)

        msg = "возможные действия:"
        buttons = [
            [types.InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.send_message(chat_id=chat_id, reply_markup=keyboard, text=msg)
        db.update_download_counter(parse_callback.replace("fop3_", ""))
    except Exception as ex:
        print(ex)
    print("everything is ok")
