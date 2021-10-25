import os
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
LIST_OF_ADMINS = os.getenv('LIST_OF_ADMINS')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)