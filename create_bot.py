from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import json
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

f = open('env.json')
config = json.load(f)
f.close()

TOKEN = config["BOT_TOKEN"]

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
