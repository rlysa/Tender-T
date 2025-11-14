from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
import time

from .forms import Form
from src.__all_func import *
from src.prompts import *


router = Router()


@router.message(Command('add_script'))
async def cmd_add_script(message: Message, state: FSMContext):
    await state.set_state(Form.add_script_name)
    await message.answer(f'Введите название сценария')


@router.message(Form.add_script_name)
async def cmd_add_script_name(message: Message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer('Слишком длинное название. Введите другое название')
        return
    await state.set_state(Form.add_script_f1)
    await state.update_data(name=message.text)
    await message.answer(f'Для создания нового сценария необходимо 2 файла')
    await message.answer(f'Отправьте файл с категориями товаров в формате txt')


@router.message(Form.add_script_f1)
async def cmd_add_script_f1(message: Message, state: FSMContext):
    if not message.document:
        await message.answer(f'Отправьте файл с категориями товаров в формате txt')
        return

    document = message.document
    file_name = document.file_name
    file_id = document.file_id
    if not file_name.endswith('.txt'):
        await message.answer(f'Отправьте файл с категориями товаров в формате txt')
        return

    bot = message.bot
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        save_path = os.path.join('../downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        return
    try:
        product_categories = get_text_from_file(save_path).lower()
        await message.answer(f'Файл отправлен на обработку')
        key_words = make_request_to_ai(prompt_get_key_words, product_categories)[0]
        await message.answer(f'Выделены ключевые слова')
    except Exception as e:
        await message.answer(f'Не удалось выделить ключевые слова')
        return
    os.remove(save_path)
    await state.set_state(Form.add_script_f2)
    await state.update_data(product_categories=product_categories.split('\n'))
    await state.update_data(key_words=key_words)
    await message.answer(f'Отправьте файл с товарами в формате xlsx')


@router.message(Form.add_script_f2)
async def cmd_add_script_f2(message: Message, state: FSMContext):
    if not message.document:
        await message.answer(f'Отправьте файл с товарами в формате xlsx')
        return

    document = message.document
    file_name = document.file_name
    file_id = document.file_id
    if not file_name.endswith('.xlsx'):
        await message.answer(f'Отправьте файл с товарами в формате xlsx')
        return

    bot = message.bot
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        save_path = os.path.join('../downloads', f'{message.from_user.id}_{file_name}')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Не удалось сохранить файл')
        return
    try:
        data = await state.get_data()
        product_categories = data['product_categories']
        file_text = get_text_from_file_by_words(save_path, product_categories[0:2])
        title = file_text['title']
        file_text.pop('title')
        products = []
        await message.answer(f'Файл отправлен на обработку')
        for category in file_text:
            answer = make_request_to_ai(prompt_get_key_info_our_products + title, file_text[category])
            for product in answer[0].strip().replace('\n\n', '\n').split('\n'):
                if len(product.strip().split(':', 1)) == 2:
                    article, name_cost = [i.strip() for i in product.strip().split(':', 1)]
                    if len(name_cost.split(';', 1)) == 2:
                        name, cost = [i.strip() for i in name_cost.split(';', 1)]
                        products.append(f'{category};{article};{name};{cost}')
        products = '\n'.join(products)
        await message.answer(f'Файл обработан')
    except Exception as e:
        await message.answer(f'Не удалось обработать файл')
        return
    # добавление в бд
    os.remove(save_path)
    await message.answer('Сценарий создан')
    await state.set_state(Form.main_st)
