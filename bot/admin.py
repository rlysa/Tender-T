from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import os

from config import ADMIN
from etl.pipeline import run_pipeline


router = Router()


@router.message(Command('get_db'))
async def cmd_get_db(message: Message):
    if message.from_user.id == ADMIN:
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        path = os.path.join(project_root, 'db', 'db', 'tender_t.db')
        await message.answer_document(document=FSInputFile(path))


@router.message(Command('run_pipeline'))
async def cmd_run_pipeline(message: Message):
    if message.from_user.id == ADMIN:
        await message.answer(ADMIN, 'Запуск сценариев')
        await run_pipeline(message.bot)
