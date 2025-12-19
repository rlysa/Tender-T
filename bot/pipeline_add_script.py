from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
import os

from bot.forms import Form
from db.db_models.loader import *
from db.db_models.db_connector import get_admins
from etl.load.loader import set_status
from etl.extract.db_connector import get_status
from utils.files import get_text_from_file

router = Router()


@router.message(Command('add_script'))
async def cmd_add_script(message: Message, state: FSMContext):
    if message.from_user.id not in get_admins():
        await message.answer('У вас нет доступа\nДля получения доступа к сценариям отправьте /get_access')
    await state.set_state(Form.add_script)
    await message.answer(f'Введите название сценария')


@router.message(Form.add_script)
async def pipeline_add_script(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'script_id' not in data:
        scr_id = await script_get_name(message)
        await state.update_data(script_id=scr_id)
        return
    script_id = data['script_id']
    if get_status('scripts', script_id) == 'name_received':
        await script_get_file_category(message, script_id)
        return
    if get_status('scripts', script_id) == 'file1_received':
        await script_get_file_products(message, script_id)
        return
    if get_status('scripts', script_id) == 'file2_received':
        await script_get_file_category(message, script_id)


async def script_get_name(message):
    if not message.text:
        await message.bot.send_message(message.from_user.id, f'Введите название сценария текстом')
        return
    if len(message.text) > 20:
        await message.bot.send_message(message.from_user.id, 'Слишком длинное название. Введите другое название')
        return

    script_id = add_new_script(message.text, message.from_user.id)
    set_status('scripts', script_id, 'name_received')

    await message.answer(f'Для создания нового сценария необходимо 2 файла')
    await message.answer(f'Отправьте файл с категориями товаров в формате txt, оформленный по шаблону')
    try:
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        path = os.path.join(project_root, 'db', 'files', 'test', 'категории.txt')
        if os.path.exists(path):
            await message.answer_document(document=FSInputFile(path))
    except Exception as e:
        await message.answer(f'Ошибка в отправке файла примера: {str(e)}')
    return script_id


async def script_get_file_category(message, script_id):
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
    file = await bot.get_file(file_id)
    file_path = file.file_path
    try:
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_1.txt')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Ошибка при сохранении файла:\n{e}')
        return

    try:
        await message.answer(f'Отправьте файл с товарами в формате xlsx, оформленный по шаблону')
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        path = os.path.join(project_root, 'db', 'files', 'test', 'товары.xlsx')
        if os.path.exists(path):
            await message.answer_document(document=FSInputFile(path))
    except Exception as e:
        await message.answer(f'Ошибка отправки файла примера: {str(e)}')
    set_status('scripts', script_id, 'file1_received')


async def script_get_file_products(message, script_id):
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
    file = await bot.get_file(file_id)
    file_path = file.file_path
    try:
        project_root = os.path.dirname(os.path.abspath('Tender-T'))
        save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_2.xlsx')
        await bot.download_file(file_path, save_path)
        await message.answer(f'Файл сохранен')
    except Exception as e:
        await message.answer(f'Ошибка при сохранении файла:\n{e}')
        return
    await message.answer(f'Файлы отправлены на обработку')
    set_status('scripts', script_id, 'file2_received')


def process(script_id):
    project_root = os.path.dirname(os.path.abspath('Tender-T'))
    save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_1.txt')
    product_categories = get_text_from_file(save_path).lower()
    categories_name_id = add_categories(script_id, product_categories.strip().split('\n'))
