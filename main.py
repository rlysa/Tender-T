import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, ADMIN
from db.db_models.session import init_db
from bot.__routers import routers
from etl.pipeline import run_pipeline

bot = Bot(token=BOT_TOKEN)
TIMER_INTERVAL = 60 * 60 * 1  # 1 час
_timer_running = False
_timer_task = None


async def timer_scenario_task():
    global _timer_running
    _timer_running = True

    try:
        while _timer_running:
            try:
                try:
                    await bot.send_message(ADMIN, 'Таймер')
                    await run_pipeline(bot)
                except Exception as e:
                    if ADMIN:
                        await bot.send_message(ADMIN, f'Ошибка в таймерной задаче: {str(e)}')
                await asyncio.sleep(TIMER_INTERVAL)
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


async def main():
    init_db()
    dp = Dispatcher(bot=bot)
    for router in routers:
        dp.include_router(router)
    await asyncio.sleep(1800)
    await asyncio.create_task(timer_scenario_task())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
