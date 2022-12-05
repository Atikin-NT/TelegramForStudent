import database as db
import botCommands as bot


def switchFun(callback_query, chat_id):
    parse_callback = str(callback_query)
    if parse_callback[3] == "0":  # одобрили
        approve(chat_id, parse_callback)
    elif parse_callback[3] == "1":  # заблокировали
        disapprove(chat_id, parse_callback)
    elif parse_callback[3] == "2":  # удалить файл
        delete_file(chat_id, parse_callback)
    elif parse_callback[3] == "3":  # скачать файл
        download_file(chat_id, parse_callback)
    else:
        bot.send_message(chat_id, "Что-то пошло не так с загрузкой файла:(")


def approve(chat_id, parse_callback):
    file_id = parse_callback.replace("fop0_", "")
    db.change_file_admin_status(file_id, True)
    bot.send_message(chat_id, "Теперь файл в свободном доступе")


def disapprove(chat_id, parse_callback):
    file_id = parse_callback.replace("fop0_", "")
    db.change_file_admin_status(file_id, False)
    bot.send_message(chat_id, "Теперь файл закрыт от свободного доступа")


def delete_file(chat_id, parse_callback):
    pass


def download_file(chat_id, parse_callback):
    file = db.get_files_by_file_id(parse_callback.replace("fop3_", ""))[0]
    file_owner = db.get_user_by_id(file[2])[0]
    download_path = f"/faculty_{file_owner[7]}/direction_{file_owner[8]}/course_{file[6]}/sub_{file[7]}/{file[1]}"
    bot.download_from_yadisk(chat_id, download_path, file[1])
    print("everything is ok")