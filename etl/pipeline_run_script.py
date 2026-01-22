from aiogram.types import FSInputFile
import os
import traceback

from etl.extract.api_data import *
from etl.transform.transformer import *
from etl.load.loader import set_date_collect
from db.db_models.db_connector import get_admins, get_cost_script
from db.db_models.loader import update_cost_script


async def run_pipeline(bot=1, restart=False):
    scripts = get_scripts()
    for script in scripts:
        cards_find, cards_relevant = 0, 0
        start_time = datetime.now(timezone(timedelta(hours=3))).strftime('%d.%m.%Y %H:%M')
        script_id, script_name = script
        try:
            if get_status('scripts', script_id) in ['created', 'finished']:
                update_cost_script(script_id, 0)
                set_status('scripts', script_id, 'cards')
            if get_status('scripts', script_id) == 'cards':
                get_cards(script_id)
                cards_find = len(get_not_looked_cards(script_id))
                set_status('scripts', script_id, 'lots')
                set_date_collect(script_id)
            if get_status('scripts', script_id) == 'lots':
                get_lots(script_id)
                set_status('scripts', script_id, 'filter')
            if get_status('scripts', script_id) == 'filter':
                filter_lots(script_id)
                set_status('scripts', script_id, 'not_relevant')
            if get_status('scripts', script_id) == 'not_relevant':
                not_relevant_cards(script_id)
                set_status('scripts', script_id, 'description')
            if get_status('scripts', script_id) == 'description':
                correct_lots_description(script_id)
            if get_status('scripts', script_id) == 'match':
                match_products_lots(script_id)
                set_status('scripts', script_id, 'relevant')
            if get_status('scripts', script_id) == 'relevant':
                relevant_cards(script_id)
                cards_relevant = len(get_relevant_cards(script_id))
                set_status('scripts', script_id, 'margin')
            if get_status('scripts', script_id) == 'margin':
                project_root = os.path.dirname(os.path.abspath('Tender-T'))
                path = os.path.join(project_root, 'db', 'files', f'{script_name}.txt')
                count_margin(script_id, path)
                set_status('scripts', script_id, 'result')
            if get_status('scripts', script_id) == 'result':
                project_root = os.path.dirname(os.path.abspath('Tender-T'))
                path = os.path.join(project_root, 'db', 'files', f'{script_name}.txt')
                for admin in get_admins():
                    if f'{admin}'[0] == '9':
                        await bot.send_message(admin, text=f'''Проверка (админ)\n {path} {os.path.exists(path)}\n Карточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}\nКоличество лотов: {get_matched_lots_count(script_id)}\n\nСтоимость: {get_cost_script(script_id)}₽''')
                for user in get_users_with_access():
                    if os.path.exists(path) and cards_relevant > 0:
                        await bot.send_document(user, document=FSInputFile(path), caption=f'''{start_time}\nСценарий "{script_name}"\n\nКарточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}\nКоличество лотов: {get_matched_lots_count(script_id)}\n\nСтоимость: {get_cost_script(script_id)}₽''')
                    else:
                        await bot.send_message(user, text=f'{start_time}\nСценарий "{script_name}"\n\nКарточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}')
                set_finish_status(script_id)
                set_success(script_id, True)
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            for admin in get_admins():
                await bot.send_message(admin, f'Ошибка при выполнении сценария: {e}')
                await bot.send_message(admin, ''.join(traceback.format_exc()))
                set_success(script_id, False)
