from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
import os
import asyncio

from .forms import Form
from src.__all_func import *
from src.prompts import *
from db.db_requests.new_script import add_new_script
from db.db_requests.get_scripts import get_scripts


router = Router()


@router.message(Command('add_script'))
async def cmd_add_script(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.add_script_name)
        await message.answer(f'Введите название сценария')
    except Exception as e:
        await message.bot.send_message(ADMIN, f'Ошибка в cmd_add_script для пользователя {message.from_user.id} {str(e)}')


@router.message(Form.add_script_name)
async def cmd_add_script_name(message: Message, state: FSMContext):
    try:
        if not message.text:
            await message.answer(f'Введите название сценария текстом')
            return
        if len(message.text) > 20:
            await message.answer('Слишком длинное название. Введите другое название')
            return
        await state.set_state(Form.add_script_f1)
        await state.update_data(name=message.text)
        await message.answer(f'Для создания нового сценария необходимо 2 файла')
        await message.answer(f'Отправьте файл с категориями товаров в формате txt, оформленный по шаблону')
        project_root = os.path.dirname(os.path.dirname(os.path.abspath('Tender-T')))
        path = os.path.join(project_root, 'files', 'test', 'категории.txt')
        await message.answer_document(document=FSInputFile(path))
    except Exception as e:
        await message.bot.send_message(ADMIN, f'Ошибка в cmd_add_script_name для пользователя {message.from_user.id}): {str(e)}')


@router.message(Form.add_script_f1)
async def cmd_add_script_f1(message: Message, state: FSMContext):
    bot = message.bot
    try:
        if not message.document:
            await message.answer(f'Отправьте файл с категориями товаров в формате txt')
            return

        document = message.document
        file_name = document.file_name
        file_id = document.file_id
        if not file_name.endswith('.txt'):
            await message.answer(f'Отправьте файл с категориями товаров в формате txt')
            return
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка  cmd_add_script_f1 для пользователя {message.from_user.id}): {str(e)}')
        return

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath('Tender-T')))
        save_path = os.path.join(project_root, 'downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        await bot.send_message(ADMIN, f'Ошибка при сохранении файла1:\n{e}')
        return
    try:
        try:
            product_categories = get_text_from_file(save_path).lower()
        except Exception as e:
            await message.answer(f'Файл пустой')
            await message.bot.send_message(ADMIN, f'Ошибка чтения файла {e}')
            return
        await message.answer(f'Файл отправлен на обработку')
        try:
            key_words = make_request_to_ai(prompt_get_key_words, bot, product_categories)
        except Exception as e:
            await message.answer('Не удалось получить ответ от AI')
            await message.bot.send_message(ADMIN, f'Ошибка AI {e}')
            return
        key_words, prompt_tokens, completion_tokens = key_words
        if key_words:
            cost = prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            await message.answer(f'Выделены ключевые слова')
        else:
            await message.answer(f'Ошибка при выделении ключевых слов')
            return
    except Exception as e:
        await message.answer(f'Не удалось выделить ключевые слова')
        await bot.send_message(ADMIN, f'Ошибка при выделении ключевых слов:\n{e}')
        return
    finally:
        os.remove(save_path)
    await state.set_state(Form.add_script_f2)

    try:
        await state.update_data(cost=cost)
        await state.update_data(product_categories=product_categories.split('\n'))
        await state.update_data(key_words=key_words)
        await message.answer(f'Отправьте файл с товарами в формате xlsx, оформленный по шаблону')
        project_root = os.path.dirname(os.path.dirname(os.path.abspath('Tender-T')))
        path = os.path.join(project_root, 'files', 'test', 'товары.xlsx')
        await message.answer_document(document=FSInputFile(path))
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка  cmd_add_script_f1 для пользователя {message.from_user.id}): {str(e)}')


@router.message(Form.add_script_f2)
async def cmd_add_script_f2(message: Message, state: FSMContext):
    bot = message.bot
    try:
        if not message.document:
            await message.answer(f'Отправьте файл с товарами в формате xlsx')
            return

        document = message.document
        file_name = document.file_name
        file_id = document.file_id
        if not file_name.endswith('.xlsx'):
            await message.answer(f'Отправьте файл с товарами в формате xlsx')
            return
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка  cmd_add_script_f2 для пользователя {message.from_user.id}): {str(e)}')
        return

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath('Tender-T')))
        save_path = os.path.join(project_root, 'downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        await bot.send_message(ADMIN, f'Ошибка при сохранении файла2:\n{e}')
        return
    try:
        data = await state.get_data()
        product_categories = data['product_categories']
        try:
            file_text = get_text_from_file(save_path).lower()
        except Exception as e:
            await message.answer(f'Файл пустой')
            await message.bot.send_message(ADMIN, f'Ошибка чтения файла {e}')
            return

        file_text = get_text_by_words(file_text, product_categories)
        if not file_text or 'title' not in file_text:
            await message.answer('Не удалось извлечь данные из файла')
            return

        title = file_text['title']
        file_text.pop('title')
        products = []
        cost_scr = 0
        await message.answer(f'Файл отправлен на обработку')

        for category in file_text:
            try:
                answer = make_request_to_ai(prompt_get_key_info_our_products + title, file_text[category])
            except Exception as e:
                await message.answer(f'Ошибка обработки категории {category}')
                await bot.send_message(ADMIN, f'Ошибка AI для категории {category}: {str(e)}')
                continue
            if not answer or len(answer) < 3:
                await message.answer(f'Ошибка обработки категории {category}')
                continue

            prompt_tokens, completion_tokens = answer[1], answer[2]
            cost_scr += prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            for product in answer[0].strip().replace('\n\n', '\n').split('\n'):
                if not product.strip():
                    continue
                if len(product.strip().split(':', 1)) == 2:
                    article, name_cost = [i.strip() for i in product.strip().split(':', 1)]
                    if len(name_cost.split(';', 1)) == 2:
                        name, cost = [i.strip() for i in name_cost.split(';', 1)]
                        products.append(f'{category};{article};{name};{cost}')
        products = '\n'.join(products)
        await message.answer(f'Файл обработан')
    except Exception as e:
        await message.answer(f'Не удалось обработать файл')
        await bot.send_message(ADMIN, f'Ошибка при выделении товаров:\n{e}')
        return
    try:
        add_new_script_to_db(data['name'], message.from_user.id, product_categories, data['key_words'], products)
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка при сохранении сценария в бд:\n{e}')
        return
    finally:
        os.remove(save_path)

    try:
        await message.answer('Сценарий создан')
        await message.answer(f'Стоимость создания сценария: {cost_scr + data['cost']}₽')
        await state.clear()

        await asyncio.sleep(60)
        documents, costs = get_tender_cards([script for script in get_scripts(message.from_user.id) if script[0] == data['name']])
        if not documents:
            await message.answer('Карточки не найдены')
        for index, doc in enumerate(documents):
            document_file = FSInputFile(doc)
            await message.answer_document(document=document_file)
            await message.answer(f'Стоимость: {costs[index]}₽')
    except Exception as e:
        await message.answer('Ошибка при поиске тендеров')

    if len(get_scripts(message.from_user.id)) == 1:
        start_scheduled_task(message.from_user.id, message.bot)


from typing import Dict
scheduled_tasks: Dict[int, asyncio.Task] = {}
_running = False


async def start_scenario_manager():
    global _running
    _running = True


def start_scheduled_task(user_id, bot):
    if user_id in scheduled_tasks:
        scheduled_tasks[user_id].cancel()
    task = asyncio.create_task(scheduled_scenario_task(user_id, bot))
    scheduled_tasks[user_id] = task


async def scheduled_scenario_task(user_id, bot):
    global _running
    while _running and get_scripts(user_id) != []:
        await asyncio.sleep(60 * 60 * 3)
        from .execute_algorithm import execute_algorithm
        await execute_algorithm(user_id, bot)


def add_new_script_to_db(name, user_id, product_categories, key_words, products):
    product_categories = '\n'.join(product_categories)
    add_new_script(name, user_id, product_categories, key_words, products)
