from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import os

from etl.pipeline import run_pipeline
from db.db_models.db_connector import get_admins, get_users_with_access


router = Router()


@router.message(Command('get_db'))
async def cmd_get_db(message: Message):
    if message.from_user.id in get_admins():
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        path = os.path.join(project_root, 'db', 'db', 'tender_t.db')
        await message.answer_document(document=FSInputFile(path))


@router.message(Command('run_scripts'))
async def cmd_run_scripts(message: Message):
    if message.from_user.id in get_admins():
        for user in get_users_with_access():
            await message.bot.send_message(user, 'Ручной запуск сценариев')
        await run_pipeline(message.bot)
