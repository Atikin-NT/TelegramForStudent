import aiogram.types

import database as db
import botCommands as ya


async def switchFun(callback_query, chat_id, bot):
    parse_callback = str(callback_query.data)
    if parse_callback[3] == "0":  # одобрили
        await approve(parse_callback, callback_query)
    elif parse_callback[3] == "1":  # заблокировали
        await disapprove(parse_callback, callback_query)
    elif parse_callback[3] == "2":  # удалить файл
        await delete_file(chat_id, parse_callback, bot)
    elif parse_callback[3] == "3":  # скачать файл
        await download_file(chat_id, parse_callback, bot)
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


async def delete_file(chat_id, parse_callback, bot):
    pass


async def download_file(chat_id, parse_callback, bot):
    file = db.get_files_by_file_id(parse_callback.replace("fop3_", ""))[0]
    file_owner = db.get_user_by_id(file[2])[0]
    download_path = f"/faculty_{file_owner[4]}/direction_{file[7]}/course_{file[3]}/sub_{file[4]}/{file[1]}"
    try:
        await ya.download_from_yadisk(chat_id, download_path, file[1], bot)
    except Exception as ex:
        print(ex)
    print("everything is ok")