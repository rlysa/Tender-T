from aiogram import Bot
from aiogram.types import FSInputFile

from src.get_tender_cards import get_tender_cards


async def execute_algorithm(user_id, bot):
    await bot.send_message(user_id, 'Поиск новых карточек')
    documents, costs = get_tender_cards(user_id)
    for doc, index in enumerate(documents):
        document_file = FSInputFile(doc)
        await bot.send_document(user_id, document=document_file)
        await bot.send_message(user_id, f'Стоимость: {costs[index]}₽')
    else:
        await bot.send_message(user_id, 'Нет новых карточек')

