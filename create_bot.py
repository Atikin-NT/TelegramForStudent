from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import json
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "env.json")
with open(new_path, 'r') as file:
    config = json.load(file)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN = config["BOT_TOKEN"]

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
