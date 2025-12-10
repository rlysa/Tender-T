from aiogram.types import FSInputFile
import os

from etl.extract.api_data import *
from etl.transform.transformer import *
from config import ADMIN


async def run_pipeline(bot):
    try:
        scripts = get_scripts(ADMIN)
        for script in scripts:
            start_time = datetime.now().strftime('%d_%m_%Y__%H_%M')
            script_id, script_name = script
            if get_status('scripts', script_id) in ['new', 'finished']:
                set_status('scripts', script_id, 'cards')
            if get_status('scripts', script_id) == 'cards':
                get_cards(script_id)
                for user in get_users_with_access():
                    await bot.send_message(user, f'Карточек найдено: {len(get_not_looked_cards(script_id))}')
                set_status('scripts', script_id, 'lots')
            if get_status('scripts', script_id) == 'lots':
                get_lots(script_id)
                set_status('scripts', script_id, 'filter')
            if get_status('scripts', script_id) == 'filter':
                filter_lots(script_id)
                set_status('scripts', script_id, 'not_relevant')
            if get_status('scripts', script_id) == 'not_relevant':
                not_relevant_cards(script_id)
                set_status('scripts', script_id, 'match')
            if get_status('scripts', script_id) == 'match':
                cost = match_products_lots(script_id)
                for user in get_users_with_access():
                    await bot.send_message(user, f'Стоимость: {cost}₽')
                set_status('scripts', script_id, 'relevant')
            if get_status('scripts', script_id) == 'relevant':
                relevant_cards(script_id)
                for user in get_users_with_access():
                    await bot.send_message(user, f'Карточек релевантно: {len(get_relevant_cards(script_id))}')
                set_status('scripts', script_id, 'margin')
            if get_status('scripts', script_id) == 'margin':
                try:
                    project_root = os.path.dirname(os.path.abspath('Tender-T'))
                    path = os.path.join(project_root, 'db', 'files', f'{script_name}__{start_time}__{get_matched_lots_count(script_id)}.txt')
                    count_margin(script_id, path)
                    for user in get_users_with_access():
                        if get_status('scripts', script_id) == 'finished':
                            await bot.send_document(user, FSInputFile(path))
                        else:
                            await bot.send_message(user, f'Нет новых карточех для сценария {script_name}')
                    os.remove(path)
                except Exception as e:
                    raise Exception(f'Ошибка в окончании пайплайна {e}')
    except Exception as e:
        await bot.send_message(ADMIN, f'Ошибка при выполнении сценария {e}')
