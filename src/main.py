import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN
from __routers import routers

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot) #, storage=storage)

for router in routers:
    dp.include_router(router)

users = set()
timer_task = None
TIMER_INTERVAL = 10800 # 3 часа


async def send_timed_message():
    message_text = f'Автоматическое сообщение'
    for user_id in [929513123, ]:
        try:
            await bot.send_message(user_id, message_text)
        except Exception as e:
            if 'bot was blocked' in str(e).lower():
                users.discard(user_id)


async def timer_worker():
    while True:
        try:

            await send_timed_message()
            await asyncio.sleep(TIMER_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            # logger.error(f'Ошибка в рабочем процессе таймера: {e}')
            await asyncio.sleep(60)


async def start_timer():
    global timer_task
    timer_task = asyncio.create_task(timer_worker())


async def on_startup():
    await start_timer()


async def on_shutdown():
    await bot.session.close()


async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())
