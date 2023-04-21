import aiogram
import yadisk
import json
from aiogram.types import InputFile
import os

directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "env.json")
with open(new_path, 'r') as file:
    config = json.load(file)

TOKEN = config["BOT_TOKEN"]
# TODO: обновление токена при истечении
YA_TOKEN = config["YA_TOKEN"]
y = yadisk.YaDisk(token=YA_TOKEN)


async def upload_to_yadisk(file_id: str,
                           download_path: list[str],
                           bot: aiogram.Bot):
    """
    Загружает файл на Яндекс диск

    :param file_id: id файла в телеграме
    :param download_path: путь для сохранения на диске
    :param bot: aiogram Bot
    :return:
    """
    file = await bot.get_file(file_id=file_id)
    filePath = file.file_path

    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{filePath}"
    path = ""
    for folder in download_path[:-1]:
        path += folder
        if not y.exists(path):
            y.mkdir(path)
    y.upload_url(download_url, path + download_path[-1])


def delete_file_from_yadisk(filePath: str):
    """
    Удаление файла с яндекс диска по определенному пути

    :param filePath: путь для удаления на диске
    :return:
    """
    try:
        y.remove(filePath, permanently=True)
    except Exception as ex:
        print(ex)


async def download_from_yadisk(chat_id: int,
                               download_path: str,
                               caption: str,
                               bot: aiogram.Bot):
    """
    Скачивание фала с яндекс диска
    
    :param chat_id: id пользователя в телеграме
    :param download_path: путь для скачивания с яндекс диска
    :param caption: имя файла, с которым отошлется в телегу
    :param bot: aiogram Bot
    :return:
    """
    file_url = y.get_download_link(download_path)
    file = InputFile.from_url(url=file_url, filename=caption)
    await bot.send_document(chat_id=chat_id, document=file)
