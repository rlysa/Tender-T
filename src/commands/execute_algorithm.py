from aiogram import Bot
from aiogram.types import FSInputFile

from src.get_tender_cards import get_tender_cards
from db.db_requests.get_scripts import get_scripts
from db.db_requests.get_uesrs import get_users_with_access
from config import ADMIN


async def execute_algorithm(user_id, bot):
    try:
        for user in get_users_with_access():
            await bot.send_message(user, 'Поиск новых карточек')
        try:
            documents, costs = get_tender_cards(get_scripts(user_id))
        except Exception as e:
            await bot.send_message(ADMIN, f'Ошибка при поиске тендеров (user {user_id}): {str(e)}')
            await bot.send_message(user_id, 'При выполнении сценария возникла ошибка')
            return
        if not documents or (isinstance(documents, list) and any('error' in str(doc).lower() for doc in documents)):
            await bot.send_message(ADMIN, f'Ошибка при выполнении сценариев:\n{documents}')
            await bot.send_message(user_id, 'При выполнении сценария возникла ошибка')
            return
        for user in get_users_with_access():
            for index, doc in enumerate(documents):
                try:
                    document_file = FSInputFile(doc)
                    await bot.send_document(user, document=document_file)
                    await bot.send_message(user, f'Стоимость: {costs[index]}₽')
                except Exception as e:
                    await bot.send_message(ADMIN, f"Ошибка отправки документа файл {doc}: {str(e)}")
                    await bot.send_message(user, f'Ошибка при отправке файла')
            else:
                await bot.send_message(user, 'Нет новых карточек')
    except Exception as e:
        await bot.send_message(ADMIN, f"Критическая ошибка в execute_algorithm: {str(e)}")
