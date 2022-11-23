import database as db
import botCommands as bot


#course//sub//name
def switchFun(callback_query, chat_id):
    parse_callback = str(callback_query).split("_")
    if len(parse_callback) == 3:
        ask_subject(chat_id, str(callback_query))
    elif len(parse_callback) == 4:
        upload(chat_id, str(callback_query))


def ask_course(document, chat_id):
    msg = "Файл какого курса обучения?"
    if document["mime_type"] != "application/pdf":
        bot.send_message("Недопустимый формат", chat_id)
        return
    fileID = document["file_id"]
    buttons = [
        {
            "text": "1",
            "callback_data": f"upload_{fileID}_1"
        },
        {
            "text": "2",
            "callback_data": f"upload_{fileID}_2"
        },
        {
            "text": "3",
            "callback_data": f"upload_{fileID}_3"
        },
        {
            "text": "4",
            "callback_data": f"upload_{fileID}_4"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def ask_subject(chat_id, callback_query):
    subjects = db.get_subjects()
    msg = "Какой предмет?"
    buttons = []
    for sub in subjects:
        buttons.append({
            "text": f"{sub[1]}",
            "callback_data": f"{callback_query}_{sub[0]}"
        })
    bot.tel_send_inlinebutton(chat_id, buttons, msg)


def upload(chat_id, callback_query):
    parse_callback = str(callback_query).split("_")
    print(parse_callback)
    bot.send_message(chat_id, "send file")
