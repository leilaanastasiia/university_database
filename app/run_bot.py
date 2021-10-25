from aiogram.utils import executor

from .bot import dp
from .db import create_table


def run_bot() -> None:
    create_table()
    executor.start_polling(dp, skip_updates=True)
