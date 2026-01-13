from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
import os

from bot.forms import Form
from db.db_models.loader import *
from db.db_models.db_connector import get_admins, get_new_script, get_categories
from etl.load.loader import set_status
from etl.extract.db_connector import get_status
from services.prompts import *
from services.ai_service import make_request_to_ai
from utils.files import get_text_from_file, get_text_by_words
from config import COST_INPUT_TOKENS, COST_OUTPUT_TOKENS

router = Router()


@router.message(Command('add_script'))
async def cmd_add_script(message: Message, state: FSMContext):
    await state.set_state(Form.add_script)
    await state.update_data(cost=0)
    if message.from_user.id not in get_admins():
        await message.answer('У вас нет доступа\nДля получения доступа к сценариям отправьте /get_access')
        return
    script_id = get_new_script(message.from_user.id)
    if script_id:
        await message.answer('Вы уже начали создание сценария')
        try:
            await pipeline_add_script(message, state)
        except Exception as e:
            await message.answer(f'Неизвестная ошибка {e}')
        return
    await state.set_state(Form.add_script)
    await message.answer(f'Введите название сценария')


@router.message(Command('cancel'), Form.add_script)
async def cancel_add_script(message: Message, state: FSMContext):
    await state.clear()
    script_id = get_new_script(message.from_user.id)
    if script_id:
        set_status('scripts', script_id, 'canceled')
        delete_files(script_id)
    await message.answer(f'Создание сценария отменено')
    delete_files(script_id)


@router.message(Form.add_script)
async def pipeline_add_script(message: Message, state: FSMContext):
    script_id = get_new_script(message.from_user.id)
    if not script_id:
        await script_get_name(message)
        return
    try:
        if get_status('scripts', script_id) == 'name_received':
            await script_get_file_category(message, script_id)
            return
        if get_status('scripts', script_id) == 'file1_received':
            await script_get_file_products(message, script_id)
            await state.update_data(cost=0)
        if get_status('scripts', script_id) != 'file1_received':
            await message.answer(f'Файлы отправлены на обработку')
            await process(script_id, message, state)
            if get_status('scripts', script_id) == 'products_received':
                await message.answer(f'Сценарий создан')
                delete_files(script_id)
                await state.clear()
                set_status('scripts', script_id, 'created')
    except Exception as e:
        await message.answer(f'Ошибка при создании сценария: {e}')


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


async def script_get_file_category(message, script_id):
    if not message.document:
        await message.answer(f'Для создания нового сценария необходимо 2 файла\n\nОтправьте файл с категориями товаров в формате txt, оформленный по шаблону')
        try:
            project_root = os.path.dirname(os.path.abspath('Tender-T'))
            path = os.path.join(project_root, 'db', 'files', 'test', 'категории.txt')
            if os.path.exists(path):
                await message.answer_document(document=FSInputFile(path))
        except Exception as e:
            await message.answer(f'Ошибка в отправке файла примера: {str(e)}')
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
        try:
            await message.answer(f'Отправьте файл с товарами в формате xlsx, оформленный по шаблону')
            project_root = os.path.dirname(os.path.abspath('Tender-T'))
            path = os.path.join(project_root, 'db', 'files', 'test', 'товары.xlsx')
            if os.path.exists(path):
                await message.answer_document(document=FSInputFile(path))
        except Exception as e:
            await message.answer(f'Ошибка отправки файла примера: {str(e)}')
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
    set_status('scripts', script_id, 'file2_received')


async def process(script_id, message, state):
    project_root = os.path.dirname(os.path.abspath('Tender-T'))
    if get_status('scripts', script_id) == 'file2_received':
        save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_1.txt')
        product_categories = get_text_from_file(save_path).lower()
        if product_categories == '':
            await message.answer('Файл с категориями пустой. Сценарий не создан')
            set_status('scripts', script_id, 'failed')
            delete_files(script_id)
            await state.clear()
            return
        categories_name_id = add_categories(script_id, product_categories.strip().split('\n'))
        add_key_words(script_id, [f'{category}: {category}' for category in categories_name_id], categories_name_id)
        set_status('scripts', script_id, 'cat_kw_received')
    if get_status('scripts', script_id) != 'file2_received':
        await message.answer('Файл 1 обработан')
        save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_2.xlsx')
        file_text = get_text_from_file(save_path).lower()
        product_categories = get_categories(script_id)
        file_text = get_text_by_words(file_text, product_categories)
        if file_text == {} or not file_text or 'title' not in file_text:
            await message.answer('Не удалось извлечь данные из файл. Сценарий не создан')
            delete_files(script_id)
            await state.clear()
            set_status('scripts', script_id, 'failed')
            return
        await message.answer('Файл 2 прочитан. Отправлен на обработку')

        title = file_text['title']
        file_text.pop('title')
        data = await state.get_data()
        cost, cur_cost = data['cost'], 0
        for category in file_text:
            status = get_status('scripts', script_id)
            if status.split('_')[-1] == f'{product_categories[category]}' or status == 'products_received':
                continue
            try:
                answer = make_request_to_ai(prompt_get_key_info_our_products + title, file_text[category])
                set_status('scripts', script_id, f'file2_process_{product_categories[category]}')
            except Exception as e:
                await message.answer(f'Ошибка AI для категории {category}: {str(e)}')
                continue
            if not answer or len(answer) < 3:
                await message.answer(f'Ошибка обработки категории {category}')
                continue
            prompt_tokens, completion_tokens = answer[1], answer[2]
            cur_cost = prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            await state.update_data(cost=(cost + cur_cost))
            add_products(script_id, answer[0].strip().split('\n'), product_categories[category])
        await message.answer(f'Стоимость создания сценария: {round(cost + cur_cost, 2)}₽')
        set_status('scripts', script_id, 'products_received')


def delete_files(script_id):
    project_root = os.path.dirname(os.path.abspath('Tender-T'))
    save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_1.txt')
    if os.path.exists(save_path):
        os.remove(save_path)
    save_path = os.path.join(project_root, 'db', 'files', f'{script_id}_2.xlsx')
    if os.path.exists(save_path):
        os.remove(save_path)