import asyncio

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, DB_NAME, ADMIN
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
    try:
        await start_scenario_manager()
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Ошибка запуска: {e}')
    finally:
        await on_shutdown()


async def run_db():
    try:
        await global_init(DB_NAME)
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка БД: {e}')


if __name__ == '__main__':
    run_db()
    asyncio.run(main())
