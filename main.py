import logging
import asyncio
import os.path

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN, DB_NAME
from src.__routers import routers
from db.db_tables.db_session import global_init
from db.db_requests.get_uesrs import get_users
from src.commands.add_script import start_scenario_manager

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot) #, storage=storage)

for router in routers:
    dp.include_router(router)

timer_task = None
TIMER_INTERVAL = 10800 # 3 часа


async def send_timed_message():
    message_text = f'Автоматическое сообщение'
    users = get_users()
    for user in users:
        try:
            await bot.send_message(user, message_text)
        except Exception as e:
            if 'bot was blocked' in str(e).lower():
                # удаление пользователя из бд
                pass


async def on_shutdown():
    await bot.session.close()


async def main():
    await start_scenario_manager()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


def run_db():
    global_init(DB_NAME)


if __name__ == '__main__':
    run_db()
    asyncio.run(main())
