from flask import Flask, request
import routes

# https://api.telegram.org/bot5546823281:AAEPLYc-UWSiffsjfBONg8J5bc6bDMumFK0/setWebhook?url=https://19d1-89-109-48-183.eu.ngrok.io
# Ni5Wmvll
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        print(request.get_json())
        msg = request.get_json()
        if "callback_query" in msg:
            routes.callback_query(msg)
        elif "edited_message" in msg:
            routes.input_text(msg)
        else:
            if ("entities" in msg["message"]) and msg["message"]["entities"][0]["type"] == 'bot_command':
                routes.commands(msg)
            else:
                routes.input_text(msg)
    return {"ok": True}


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)


#  обработчик неизвестных команд типа /<command>  сделал!
#  в середине регистрации ее можно прервать пользователь запишится, а данные нет
#  обработчик редактированных сообщений edited_message done!
#  переименование файла при скачивании
