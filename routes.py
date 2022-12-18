import botCommands as bot
import database as db
import scenarios.register as reg
import scenarios.findUser as findUser
import scenarios.showFiles as showFl
import scenarios.profileMenu as profileMenu
import scenarios.uploadFile as uploadFile
import scenarios.fileOper as fileOper


def callback_query(msg):
    print(msg)
    if "reg" in msg["callback_query"]["data"]:
        reg.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"], msg["callback_query"]["message"]["message_id"] + 1)
    elif "sfl" in msg["callback_query"]["data"]:
        showFl.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "upld" in msg["callback_query"]["data"]:
        uploadFile.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "prf" in msg["callback_query"]["data"]:
        profileMenu.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "fop" in msg["callback_query"]["data"]:
        fileOper.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "main_menu" in msg["callback_query"]["data"]:
        profileMenu.show_menu(msg["callback_query"]["message"]["chat"]["id"], msg["callback_query"]["data"])
    else:
        bot.send_message(msg["callback_query"]["message"]["chat"]["id"], "Неизвестная команда")


def commands(msg):
    username = msg["message"]["chat"]["first_name"]
    if "username" in msg["message"]["chat"]:
        username = msg["message"]["chat"]["username"]

    if msg["message"]["text"] == "/start":
        hello_text = "Welcome to this bot\n Type /login to login"
        bot.send_message(msg["message"]["chat"]["id"], hello_text)
        return
    elif msg["message"]["text"] == "/login":
        reg.start(msg["message"]["chat"]["id"], username, msg["message"]["message_id"] + 1)
        return
    user = db.get_user_by_username(username)
    if len(user) == 0:
        bot.send_message(username, "Вас нет в системе!\nСначала зарегистрируйтесь с помощью "
                                                             "команды /login")
        return
    if msg["message"]["text"] == "/find":
        findUser.start(msg["message"]["chat"]["id"])
    elif msg["message"]["text"] == "/menu":
        profileMenu.show_menu(msg["message"]["chat"]["id"], msg["message"]["message_id"] + 1)
    else:
        bot.send_message(msg["message"]["chat"]["id"], "Неизвестная команда")


def input_text(msg):
    if "text" in msg["message"]:
        if msg["message"]["text"][0] == "@":
            findUser.find_by_username(msg["message"]["chat"]["id"], msg["message"]["text"])
        elif "Мр" in msg["message"]["text"]:
            bot.send_message(msg["message"]["chat"]["id"], "Приветики, мое солнышко 😘")
        else:
            showFl.list_files_by_name(msg["message"]["chat"]["id"], msg["message"]["text"])
    elif "document" in msg["message"]:
        uploadFile.upload_document(msg["message"]["document"], msg["message"]["chat"]["id"])
    else:
        try:
            bot.send_message(msg["message"]["chat"]["id"], "недопустимое сообщение")
        except Exception as ex:
            print(ex)
