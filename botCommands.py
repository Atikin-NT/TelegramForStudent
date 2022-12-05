import requests
import yadisk

TOKEN = "5546823281:AAEPLYc-UWSiffsjfBONg8J5bc6bDMumFK0"
# TODO: обновление токена при истечении
TOKEN_YA = "y0_AgAAAABmapUwAAizegAAAADU3hxhdlyBRNdUQ6KD1CMUNSmhh1Ft7yE"
ClientID = "daec211d1a30442387e86642832efd60"
ClientSecret = "970e8b1633cc499e8f3898c50ae3b006"
y = yadisk.YaDisk(token=TOKEN_YA)
print(y.check_token())
print(y.get_disk_info())
# Redirect url https://oauth.yandex.ru/verification_code


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
    tel_send_document(chat_id, file_url, caption)

