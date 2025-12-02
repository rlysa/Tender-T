import asyncio

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, DB_NAME, ADMIN
from src.__routers import routers
from db.db_tables.db_session import global_init
from src.commands.execute_algorithm import execute_algorithm


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

for router in routers:
    dp.include_router(router)

TIMER_INTERVAL = 10800 # 3 часа
_timer_running = False
_timer_task = None


async def timer_scenario_task():
    global _timer_running
    _timer_running = True

    try:
        print(1)
        while _timer_running:
            try:
                try:
                    await execute_algorithm(ADMIN, bot)
                except Exception as e:
                    if ADMIN:
                        await bot.send_message(ADMIN, f'Ошибка в таймерной задаче: {str(e)}')
                await asyncio.sleep(10)
            except Exception as e:
                if ADMIN:
                    await bot.send_message(ADMIN, f'Критическая ошибка в таймерной задаче: {str(e)}')
                await asyncio.sleep(300)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        if ADMIN:
            await bot.send_message(ADMIN, f'Фатальная ошибка в таймерной задаче: {str(e)}')
    finally:
        _timer_running = False


async def on_shutdown():
    await bot.session.close()


async def run_db():
    try:
        global_init(DB_NAME)
        asyncio.create_task(timer_scenario_task())
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка БД: {e}')


async def main():
    try:
        await run_db()
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Ошибка запуска: {e}')
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())
