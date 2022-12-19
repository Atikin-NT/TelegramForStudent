import requests
import yadisk
import json

f = open('env.json', 'r')
config = json.load(f)

TOKEN = config["BOT_TOKEN"]
# TODO: обновление токена при истечении
YA_TOKEN = config["YA_TOKEN"]
y = yadisk.YaDisk(token=YA_TOKEN)


def send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "markdown"}
    requests.post(url, data=data)


def tel_send_inlinebutton(chat_id, buttons, text, message_id=None):
    method = "sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'markdown',
        'reply_markup': {
            "inline_keyboard": [

            ]
        }
    }
    if message_id:
        method = "editMessageText"
        payload["message_id"] = message_id
    url = f'https://api.telegram.org/bot{TOKEN}/{method}'

    for button in buttons:
        new_button = [{
            "text": button["text"],
            "callback_data": button["callback_data"]
        }]
        payload["reply_markup"]["inline_keyboard"].append(new_button)

    requests.post(url, json=payload).json()


def tel_send_document(chat_id, file_url, caption):
    method = "sendDocument"
    url = f'https://api.telegram.org/bot{TOKEN}/{method}'

    payload = {
        "chat_id": chat_id,
        "document": file_url,
        "caption": caption,

    }

    return requests.post(url, json=payload)


def upload_to_yadisk(file_id, download_path):
    method = "getFile"
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = {"file_id": file_id}
    filePath = requests.post(url, data=data).json()
    print(filePath)
    filePath = filePath["result"]["file_path"]

    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{filePath}"
    path = ""
    for folder in download_path[:-1]:
        path += folder
        if not y.exists(path):
            y.mkdir(path)
    y.upload_url(download_url, path + download_path[-1])


def download_from_yadisk(chat_id, download_path, caption):
    file_url = y.get_download_link(download_path)
    print(file_url)
    tel_send_document(chat_id, file_url, caption)

