from aiogram.types import FSInputFile
import os

from etl.extract.api_data import *
from etl.transform.transformer import *
from db.db_models.db_connector import get_admins


async def run_pipeline(bot, restart=False):
    try:
        scripts = get_scripts()
        for script in scripts:
            cards_find, cost, cards_relevant = 0, 0, 0
            start_time = datetime.now().strftime('%d.%m.%Y %H:%M')
            script_id, script_name = script
            if get_status('scripts', script_id) in ['new', 'finished']:
                set_status('scripts', script_id, 'cards')
            if get_status('scripts', script_id) == 'cards':
                get_cards(script_id)
                cards_find = len(get_not_looked_cards(script_id))
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
                        await bot.send_message(admin, text=f'''Проверка (админ)\n {path} {os.path.exists(path)}\n Карточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}\nКоличество лотов: {get_matched_lots_count(script_id)}\n\nСтоимость: {round(cost, 2)}₽''')
                for user in get_users_with_access():
                    if os.path.exists(path) and cards_relevant > 0:
                        await bot.send_document(user, document=FSInputFile(path), caption=f'''{start_time}\nСценарий "{script_name}"\n\nКарточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}\nКоличество лотов: {get_matched_lots_count(script_id)}\n\nСтоимость: {round(cost, 2)}₽''')
                    else:
                        await bot.send_message(user, text=f'{start_time}\nСценарий "{script_name}"\n\nКарточек найдено: {cards_find}\nКарточек релевантно: {cards_relevant}')
                set_finish_status(script_id)
                set_status('scripts', script_id, 'finished')
    except Exception as e:
        for admin in get_admins():
            await bot.send_message(admin, f'Ошибка при выполнении сценария: {e}')
