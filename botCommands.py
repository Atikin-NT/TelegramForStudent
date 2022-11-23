import requests

TOKEN = "5546823281:AAEPLYc-UWSiffsjfBONg8J5bc6bDMumFK0"


def send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "markdown"}
    requests.post(url, data=data)


def tel_send_inlinebutton(chat_id, buttons, text):
    method = "sendMessage"
    url = f'https://api.telegram.org/bot{TOKEN}/{method}'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            "inline_keyboard": [[

            ]]
        }
    }

    for button in buttons:
        new_button = {
            "text": button["text"],
            "callback_data": button["callback_data"]
        }
        payload["reply_markup"]["inline_keyboard"][0].append(new_button)

    requests.post(url, json=payload)
