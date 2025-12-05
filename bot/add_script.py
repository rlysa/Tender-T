from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
import os

from bot.forms import Form
from config import ADMIN, COST_INPUT_TOKENS, COST_OUTPUT_TOKENS
from db.db_models.loader import *
from utils.files import get_text_from_file, get_text_by_words
from services.ai_service import make_request_to_ai
from services.prompts import *


router = Router()


@router.message(Command('add_script'))
async def cmd_add_script(message: Message, state: FSMContext):
    try:
        if not message.from_user.id == ADMIN:
            await message.answer('У вас нет доступа\nДля получения доступа к сценариям отправьте /get_access')
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
        script_id = add_new_script(message.text, message.from_user.id)

        await state.set_state(Form.add_script_f1)
        await state.update_data(script_id=script_id)
        await message.answer(f'Для создания нового сценария необходимо 2 файла')
        await message.answer(f'Отправьте файл с категориями товаров в формате txt, оформленный по шаблону')
        project_root = os.path.dirname(os.path.abspath('Tender-ETL'))
        path = os.path.join(project_root, 'db', 'files', 'test', 'категории.txt')
        if os.path.exists(path):
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
        project_root = os.path.dirname(os.path.abspath('Tender-ETL'))
        save_path = os.path.join(project_root, 'db', 'files', 'downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        await bot.send_message(ADMIN, f'Ошибка при сохранении файла1:\n{e}')
        return
    try:
        data = await state.get_data()
        try:
            product_categories = get_text_from_file(save_path).lower()
            categories_name_id = add_categories(data['script_id'], product_categories.strip().split('\n'))
        except Exception as e:
            await message.answer(f'Ошибка чтения файла {e}')
            await message.bot.send_message(ADMIN, f'Ошибка чтения файла {e}')
            return
        await message.answer(f'Файл отправлен на обработку')
        try:
            keywords = make_request_to_ai(prompt_get_key_words, product_categories)
        except Exception as e:
            await message.answer('Не удалось получить ответ от AI')
            await message.bot.send_message(ADMIN, f'Ошибка AI {e}')
            return
        keywords, prompt_tokens, completion_tokens = keywords
        if keywords:
            add_key_words(data['script_id'], keywords.strip().split('\n'), categories_name_id)
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
        await state.update_data(categories_name_id=categories_name_id)
        await message.answer(f'Отправьте файл с товарами в формате xlsx, оформленный по шаблону')
        project_root = os.path.dirname(os.path.abspath('Tender-ETL'))
        path = os.path.join(project_root, 'db', 'files', 'test', 'товары.xlsx')
        if os.path.exists(path):
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
        project_root = os.path.dirname(os.path.abspath('Tender-ETL'))
        save_path = os.path.join(project_root, 'db', 'files', 'downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        await bot.send_message(ADMIN, f'Ошибка при сохранении файла2:\n{e}')
        return
    try:
        data = await state.get_data()
        product_categories = data['categories_name_id']
        try:
            file_text = get_text_from_file(save_path).lower()
        except Exception as e:
            await message.answer(f'Ошибка чтения файла')
            await message.bot.send_message(ADMIN, f'Ошибка чтения файла {e}')
            return

        file_text = get_text_by_words(file_text, product_categories)
        if file_text == {} or not file_text or 'title' not in file_text:
            await message.answer('Не удалось извлечь данные из файла')
            return

        title = file_text['title']
        file_text.pop('title')
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
            add_products(data['script_id'], answer[0].strip().split('\n'), product_categories[category])
        await message.answer(f'Файл обработан')
    except Exception as e:
        await message.answer(f'Не удалось обработать файл')
        await bot.send_message(ADMIN, f'Ошибка при выделении товаров:\n{e}')
        return
    os.remove(save_path)

    try:
        await message.answer('Сценарий создан')
        await message.answer(f'Стоимость создания сценария: {cost_scr + data['cost']}₽')
        await state.clear()
    except Exception as e:
        await message.answer('Ошибка при поиске тендеров')
