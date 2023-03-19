import json
import logging
from aiogram import Bot, Dispatcher, executor, types
import database as db
import scenarios.profileMenu as profileMenu
import scenarios.register as reg
import scenarios.showFiles as showFl
import scenarios.uploadFile as uploadFile
import scenarios.fileOper as fileOper
import scenarios.findUser as findUser
import scenarios.admin as admin

f = open('env.json')
config = json.load(f)
f.close()

TOKEN = config["BOT_TOKEN"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.callback_query_handler()
async def prfMenu(callback: types.CallbackQuery):
    callback_data = callback.data
    if "reg" in callback_data:
        await reg.switchFun(callback, bot)
    elif "sfl" in callback_data:
        await showFl.switchFun(callback, bot)
    elif "upld" in callback_data:
        await uploadFile.switchFun(callback, bot)
    elif "prf" in callback_data:
        await profileMenu.switchFun(callback)
    elif "fop" in callback_data:
        await fileOper.switchFun(callback, bot)
    elif "adm" in callback_data:
        await admin.switchFun(callback_data, callback.from_user.id, bot)
    elif "main_menu" in callback_data:
        await profileMenu.show_menu(callback.from_user.id, callback.message.message_id, True)
    else:
        await callback.answer("Неизвестная команда")
    await callback.answer()


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await bot.send_message(msg.chat.id, "Welcome to this bot\n Type /login to login")


@dp.message_handler(commands=['dev'])
async def start(msg: types.Message):
    print("start")
    file = await bot.get_file(file_id="sdfsdf")
    print(file)

@dp.message_handler(commands=['login'])
async def start(msg: types.Message):
    print("start_reg")
    await reg.start(msg.chat.id, msg.from_user.username, msg.message_id, bot)


@dp.message_handler(commands=['menu'])
async def start(msg: types.Message):
    print("profileMenu")
    await profileMenu.show_menu(msg.chat.id, msg.message_id + 1, False)


@dp.message_handler(content_types=['document'])
async def send_file(msg: types.Message):
    if msg.content_type == 'document':
        await uploadFile.upload_document(msg.document, msg.chat.id, msg.message_id, bot)


@dp.message_handler()
async def input_text(msg: types.Message):
    session = db.get_session(msg.chat.id)
    message = msg.text
    if message[0] == "@":
        await findUser.find_by_username(msg.chat.id, msg.text, msg.message_id, bot)
    elif "Мр" in message:
        await bot.send_message(msg.chat.id, "Приветики, мое солнышко 😘")
    elif len(session) != 0 and len(session[0]) != 0 and session[0][1] == "massive_message":
        print("send_massive_mess")
    elif len(session) != 0 and len(session[0]) != 0:
        if len(session[0][1].split("|")) == 4:
            await uploadFile.rename_file_new_name(msg.chat.id, msg.message_id, msg.text, bot)
        # bot.send_massive_message(msg["message"]["chat"]["id"], msg["message"]["text"])
    else:
        pass
        # print("showFl")
        # await showFl.list_files_by_name(msg.chat.id, msg.text, msg.message_id + 1, bot)
    print(message)


if __name__ == '__main__':
    logging.basicConfig(filename="log.txt",
                        level=logging.INFO,
                        format="%(asctime)s %(message)s",
                        filemode="w")
    executor.start_polling(dp, skip_updates=True)
