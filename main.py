import asyncio
from aiogram import Bot, Dispatcher
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
                if ADMIN:
                    await bot.send_message(ADMIN, 'Запуск сценариев')
                await run_pipeline(bot)


            except Exception as e:
                if ADMIN:
                    try:
                        await bot.send_message(ADMIN, 'Ошибка в таймере')
                    except:
                        pass

            wait_seconds = TIMER_INTERVAL
            while wait_seconds > 0 and _timer_running:
                chunk = min(5, wait_seconds)
                await asyncio.sleep(chunk)
                wait_seconds -= chunk

    except asyncio.CancelledError:
        raise
    except Exception as e:
        if ADMIN:
            try:
                await bot.send_message(ADMIN, f'Критическая ошибка таймера: {str(e)[:4000]}')
            except:
                pass
    finally:
        _timer_running = False


async def on_startup():
    global _timer_task
    _timer_task = asyncio.create_task(timer_scenario_task())


async def on_shutdown():
    global _timer_running, _timer_task
    _timer_running = False

    if _timer_task and not _timer_task.done():
        _timer_task.cancel()
        try:
            await _timer_task
        except asyncio.CancelledError:
            pass

    await bot.session.close()


async def main():
    try:
        init_db()
        dp = Dispatcher(bot=bot)
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        for router in routers:
            dp.include_router(router)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        raise
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())