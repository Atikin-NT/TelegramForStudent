import database as db
import botCommands as bot


def switchFun(callback_query, chat_id):
    callback_query = str(callback_query)
    if callback_query[3] == "0":
        main_menu(chat_id, callback_query)
    elif callback_query[3] == "1":
        send_message_for_all_users(chat_id, callback_query)
    else:
        bot.send_message(chat_id, "неизвестная команда")


def main_menu(chat_id, callback_query):
    message_id = callback_query.replace("adm0_", "")
    msg = "Меню:"
    buttons = [
        {
            "text": "Рассылка сообщения",
            "callback_data": f"adm1_{message_id}"
        }
    ]
    bot.tel_send_inlinebutton(chat_id, buttons, msg, message_id)


def send_message_for_all_users(chat_id, callback_query):
    db.create_new_session(chat_id, "massive_message")
    message_id = callback_query.replace("adm1_", "")
    msg = "Введите текст сообщения:"
    bot.tel_send_inlinebutton(chat_id, [], msg, message_id)

