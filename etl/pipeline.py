from etl.extract.api_data import *
from etl.transform.transformer import *
from config import ADMIN


async def run_pipeline(bot):
    scripts = get_scripts(ADMIN)
    for script in scripts:
        script_id, script_name = script
        if get_status('scripts', script_id) in ['new', 'finished']:
            set_status('scripts', script_id, 'cards')
        if get_status('scripts', script_id) == 'cards':
            get_cards(script_id)
            set_status('scripts', script_id, 'lots')
        if get_status('scripts', script_id) == 'lots':
            get_lots(script_id)
            set_status('scripts', script_id, 'filter')
        if get_status('scripts', script_id) == 'filter':
            filter_lots(script_id)
            set_status('scripts', script_id, 'match')
        if get_status('scripts', script_id) == 'match':
            match_products_lots(script_id)
            set_status('scripts', script_id, 'margin')


    # for script in scripts:
    #     script_id = script[0]
    #     try:
    #         key_words_file_text = get_text_from_file(script[2])
    #         key_words_map = {}
    #         for pair in key_words_file_text.split('\n'):
    #             if len(pair.split(':')) == 2:
    #                 category, word = [i.strip() for i in pair.split(':', 1)]
    #                 if category not in key_words_map:
    #                     key_words_map[category] = []
    #                 key_words_map[category].append(word)
    #
    #         cards_data, _ = get_cards([word for kw in key_words_map for word in key_words_map[kw]][0:1])
    #         looked_cards = get_text_from_file(script[4]).split('\n')
    #         not_looked_cards = [card for card in cards_data if card not in looked_cards]
    #         if not not_looked_cards:
    #             continue
    #         card_region, card_lots_data, lots_data = get_lots([[card, cards_data[card]['link']] for card in not_looked_cards])
    #
    #         for card in card_region:
    #             cards_data[card]['region'] = cards_data[card]['region']
    #         save_cards(cards_data)
    #         save_lots(lots_data, card_lots_data)
    #
    #         transform_output = transformer.transform_cards(script, cards_data, card_lots_data, lots_data)
    #
    #         result_text, cost, looked_cards = transform_output
    #
    #         if not result_text:
    #             raise Exception(f"Сценарий {script[1]}: Новых конкурсных карточек не найдено.")
    #             continue
    #
    #
    #         # file_path = load_results.load_and_update_viewed(
    #         #     script_id=script[0],
    #         #     result_text=result_text,
    #         #     viewed_cards=new_viewed_cards_ids,
    #         #     viewed_cards_file_path=script[4]
    #         # )
    #         #
    #         # successful_files.append(file_path)
    #         # total_costs.append(cost)
    #
    #         # db_connector.update_run_status(script_id, 'Success') # Опционально: запись успеха
    # #
    #     except Exception as e:
    #         # send_error_to_admin(f"Ошибка в пайплайне для сценария ID {script_id}: {e}")
    #         print(f"Ошибка в пайплайне для сценария ID {script_id}: {e}")
    #         # db_connector.update_run_status(script_id, 'Error', str(e)) # Опционально: запись ошибки
    #
    # return [successful_files, total_costs]
