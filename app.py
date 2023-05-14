import logging
from time import sleep
from aiogram import executor, types
import scenarios.profileMenu as profileMenu
import scenarios.register as reg
import scenarios.showFiles as showFl
import scenarios.uploadFile as uploadFile
import scenarios.fileOper as fileOper
import scenarios.admin as admin
from create_bot import dp, bot

reg.register_handle_register(dp)
profileMenu.register_handle_profileMenu(dp)
admin.register_handle_admin(dp)
showFl.register_handle_showFiles(dp)
uploadFile.register_handle_uploadFile(dp)
fileOper.register_handle_fileOper(dp)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await bot.send_message(msg.chat.id, "Добро пожаловать.\nЭтот бот создан для того, чтобы оказать поддержку в процессе твоего обучения.\nУ тебя все получиться ʕ ᵔᴥᵔ ʔ")
    sleep(5)
    await bot.send_message(msg.chat.id,"Нажми /login чтобы пройти регистрацию.")

if __name__ == '__main__':
    logging.basicConfig(filename="app.log",
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        filemode="w")
    executor.start_polling(dp, skip_updates=True)
