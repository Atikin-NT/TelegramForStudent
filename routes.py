import botCommands as bot
import scenarios.register as reg
import scenarios.findUser as findUser
import scenarios.showFiles as showFl
import scenarios.profileMenu as profileMenu
import scenarios.uploadFile as uploadFile


def callback_query(msg):
    if "reg" in msg["callback_query"]["data"]:
        reg.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "sfl" in msg["callback_query"]["data"]:
        showFl.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "upload" in msg["callback_query"]["data"]:
        uploadFile.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "prf" in msg["callback_query"]["data"]:
        profileMenu.switchFun(msg["callback_query"]["data"], msg["callback_query"]["message"]["chat"]["id"])
    elif "main_menu" == msg["callback_query"]["data"]:
        profileMenu.show_menu(msg["callback_query"]["message"]["chat"]["id"])
    else:
        bot.send_message(msg["callback_query"]["message"]["chat"]["id"], "Неизвестная команда")


def commands(msg):
    if msg["message"]["text"] == "/start":
        hello_text = "Welcome to this bot\n Type /login to login"
        bot.send_message(msg["message"]["chat"]["id"], hello_text)
    elif msg["message"]["text"] == "/login":
        reg.start(msg["message"]["chat"]["id"], msg["message"]["chat"]["username"])
    elif msg["message"]["text"] == "/find":
        findUser.start(msg["message"]["chat"]["id"])
    elif msg["message"]["text"] == "/menu":
        profileMenu.show_menu(msg["message"]["chat"]["id"])
    else:
        bot.send_message(msg["callback_query"]["message"]["chat"]["id"], "Неизвестная команда")


def input_text(msg):
    if "text" in msg["message"]:
        if msg["message"]["text"][0] == "@":
            findUser.find_by_username(msg["message"]["chat"]["id"], msg["message"]["text"])
    elif "document" in msg["message"]:
        uploadFile.ask_course(msg["message"]["document"], msg["message"]["chat"]["id"])
    else:
        bot.send_message(msg["message"]["chat"]["id"], "недопустимое сообщение")

