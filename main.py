import asyncio

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, DB_NAME
from src.__routers import routers
from db.db_tables.db_session import global_init
from src.commands.add_script import start_scenario_manager


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

for router in routers:
    dp.include_router(router)

timer_task = None
TIMER_INTERVAL = 10800 # 3 часа


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
