import database as db
import botCommands as bot


def switchFun(callback_query, chat_id):
    parse_callback = str(callback_query)
    if parse_callback[4] == "0":  # узнали курс
        ask_subject(chat_id, parse_callback)
    elif parse_callback[4] == "1":  # узнали предмет
        upload_msg(chat_id, parse_callback)
    else:
        bot.send_message(chat_id, "Что-то пошло не так с загрузкой файла:(")


def ask_course(chat_id):
    msg = "Файл какого курса обучения?"
    buttons = [
        {
            "text": "1",
            "callback_data": "upld0_1"
        },
        {
            "text": "2",
            "callback_data": "upld0_2"
        },
        {
            "text": "3",
            "callback_data": "upld0_3"
        },
        {
            "text": "4",
            "callback_data": "upld0_4"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_subject(chat_id, course):
    db.create_new_session(chat_id, course.replace("upld0_", ""))
    subjects = db.get_subjects()
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append({
            "text": f"{sub[1]}",
            "callback_data": f"upld1_{sub[0]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def upload_msg(chat_id, subject):
    db.update_session(chat_id, subject.replace("upld1", ""))
    bot.send_message(chat_id, "send file")


# Факультет/напрвление/курс/предмет
def upload_document(document, chat_id):
    session = db.get_session(chat_id)  # [(708133213, '2_1')]
    db.delete_session(chat_id)
    if len(session) == 0 or len(session[0]) == 0:
        bot.send_message(chat_id, "error in upload")
        return

    user_info = db.get_user_by_id(chat_id)[0]  # [(708133213, 'AtikinNT', datetime.date(2022, 11, 21), 0, False, [0, 0, 0, 0, 0], 0, 0, 0, 2)]
    data = session[0][1].split("_")  # [2(course), 1(subject)]
    download_path = [
        f"/faculty_{user_info[7]}",
        f"/direction_{user_info[8]}",
        f"/course_{data[0]}",
        f"/sub_{data[1]}",
        f"/{document['file_name']}",
    ]

    print(document)
    if document["mime_type"] != "application/pdf":
        bot.send_message("Недопустимый формат (пока только pdf)", chat_id)
        return
    fileID = document["file_id"]
    db.insert_file(document['file_name'], chat_id, data[0], data[1])
    bot.upload_to_yadisk(fileID, download_path)
    bot.send_message(chat_id, "Файл загружен")

