from config import COST_INPUT_TOKENS, COST_OUTPUT_TOKENS
from etl.extract.db_connector import *
from etl.load.loader import *
from services.ai_service import make_request_to_ai
from services.prompts import promt_count_margin


def filter_lots(script_id):
    lots = get_not_filtered_lots(script_id)
    categories = get_categories(script_id)
    for category in categories:
        for lot in lots:
            if any(word[:-2:].lower() in lot[1].lower() for word in category[1].split(' ')):
                set_category(lot[0], category[0])
            else:
                set_status('lots', lot[0], 'finished')


def match_products_lots(script_id):
    categories = get_categories(script_id)
    cost = 0
    for category in categories:
        lots = get_filtered_lots(script_id, category[0])
        products = get_products(script_id, category[0])
        lots_text = '\n'.join(lots)
        products_text = '\n'.join(products)
        answer = make_request_to_ai(promt_count_margin.replace('//Заменить//', products_text), lots_text)
        true_lots = []
        if answer:
            prompt_tokens, completion_tokens = answer[1], answer[2]
            cost += prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            margin_info = answer[0].strip().replace('\n\n', '\n')
            if margin_info:
                for pair in margin_info.split('\n'):
                    if len(pair.strip().split(':', 1)) == 2:
                        lot, product = [i.strip() for i in pair.split(':', 1)]
                        if product in products_text:
                            lots.append(lot)
                            set_match_product(lot, product)
        for lot in lots:
            if lot.split(':')[0] not in true_lots:
                set_status('lots', lot.split(':')[0], 'finished')

