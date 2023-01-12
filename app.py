import json
# import time
import logging
# import routes
# import requests
from aiogram import Bot, Dispatcher, executor, types
# import routes
import database as db
# import scenarios.findUser as findUser
import scenarios.profileMenu as profileMenu

f = open('env.json')
config = json.load(f)
f.close()

TOKEN = config["BOT_TOKEN"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await bot.send_message(msg.chat.id, "Welcome to this bot\n Type /login to login")


@dp.message_handler(commands=['login'])
async def start(msg: types.Message):
    print("start_reg")
    # reg.start(msg["message"]["chat"]["id"], username, msg["message"]["message_id"] + 1)


@dp.message_handler(commands=['menu'])
async def start(msg: types.Message):
    print("profileMenu")
    await profileMenu.show_menu(msg.chat.id, msg.message_id + 1)


@dp.message_handler()
async def input_text(msg: types.Message):
    session = db.get_session(msg.chat.id)
    message = msg.text
    print(msg.entities)
    mention_user = None
    entities = msg.entities or []
    for item in entities:
        if item.type == "mention":
            print(item)
            mention_user = item.extract(msg.text)
    print(mention_user)
    if message[0] == "@":
        print("findUser")
        # findUser.find_by_username(msg.chat.id, msg.text, msg.message_id)
    elif "Мр" in message:
        await bot.send_message(msg.chat.id, "Приветики, мое солнышко 😘")
    elif len(session) != 0 and len(session[0]) != 0 and session[0][1] == "massive_message":
        print("send_massive_mess")
        # bot.send_massive_message(msg["message"]["chat"]["id"], msg["message"]["text"])
    else:
        print("showFl")
        # showFl.list_files_by_name(msg["message"]["chat"]["id"], msg["message"]["text"],
        #                           msg["message"]["message_id"] + 1)
    if msg.document is not None:
        print("uploadFile")
        # uploadFile.upload_document(msg["message"]["document"], msg["message"]["chat"]["id"])
    print(message)


if __name__ == '__main__':
    logging.basicConfig(filename="log.txt",
                        level=logging.INFO,
                        format="%(asctime)s %(message)s",
                        filemode="w")
    executor.start_polling(dp, skip_updates=True)
