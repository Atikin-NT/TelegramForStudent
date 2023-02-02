import aiogram
import yadisk
import json
from aiogram.types import InputFile

f = open('env.json', 'r')
config = json.load(f)

TOKEN = config["BOT_TOKEN"]
# TODO: обновление токена при истечении
YA_TOKEN = config["YA_TOKEN"]
y = yadisk.YaDisk(token=YA_TOKEN)


async def upload_to_yadisk(file_id, download_path, bot: aiogram.Bot):
    file = await bot.get_file(file_id=file_id)
    filePath = file.file_path

    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{filePath}"
    path = ""
    for folder in download_path[:-1]:
        path += folder
        if not y.exists(path):
            y.mkdir(path)
    y.upload_url(download_url, path + download_path[-1])


def delete_file_from_yadisk(filePath):
    try:
        y.remove(filePath, permanently=True)
    except Exception as ex:
        print(ex)


async def download_from_yadisk(chat_id, download_path, caption, bot: aiogram.Bot):
    file_url = y.get_download_link(download_path)
    print(file_url)
    file = InputFile.from_url(url=file_url, filename=caption)
    await bot.send_document(chat_id=chat_id, document=file)


# def send_massive_message(user_id, message):
#     db.delete_session(user_id)
#     users = db.get_all_users()
#     for user in users:
#         send_message(user[0], message, False)
#     send_message(user_id, f"Сообщение отправлено {len(users)} пользователям")
