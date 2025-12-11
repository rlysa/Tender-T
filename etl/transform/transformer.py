from config import COST_INPUT_TOKENS, COST_OUTPUT_TOKENS
from etl.extract.db_connector import *
from etl.load.loader import *
from services.ai_service import make_request_to_ai
from services.prompts import promt_count_margin
from utils.files import update_file


def filter_lots(script_id):
    lots = get_not_filtered_lots(script_id)
    categories = get_categories(script_id)
    for category in categories:
        for lot in lots:
            if any(word[:-2:].lower() in lot[1].lower() for word in category[1].split(' ')):
                set_category(lot[0], category[0])
                set_status('lots', lot[0], 'filtered')
            else:
                set_status('lots', lot[0], 'finished')


def not_relevant_cards(script_id):
    cards = get_all_cards(script_id)
    for card in cards:
        lots = get_filtered_lots_for_card(card)
        if not lots:
            set_status('cards', card, 'finished')
            set_relevant(card, False)
        else:
            set_status('cards', card, 'processed')


def match_products_lots(script_id):
    categories = get_categories(script_id)
    cost = 0
    for category in categories:
        lots = get_filtered_lots(script_id, category[0])
        products = get_products(script_id, category[0])
        lots_text = '\n'.join(lots)
        products_text = '\n'.join(products)
        if lots:
            answer = make_request_to_ai(promt_count_margin.replace('//Заменить//', products_text), lots_text)
        else:
            continue
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
                set_status('lots', lot.split(':')[0], 'matched')
    return cost


def relevant_cards(script_id):
    cards = get_filtered_cards(script_id)
    for card in cards:
        lots = get_matched_lots_for_card(card)
        if not lots:
            set_status('cards', card, 'finished')
            set_relevant(card, False)
        else:
            set_relevant(card, True)


def count_margin(script_id, path):
    cards = get_relevant_cards(script_id)
    for card in cards:
        result = ''
        card_id, card_number, card_name, card_cost, card_region, card_link = card
        lots_products = get_matched_lots_products_for_card(card_id)
        other_lots = get_not_matched_lots(card_id)

        margin, coverage = 0, 0
        result += f'{card_name}\n{card_link}\nОбщая сумма закупки: {card_cost}₽\nРегион: {card_region}'
        for lot in lots_products:
            l_id, l_article, l_name, l_description, l_count, l_cost, p_article, p_name, p_cost = lot
            product_margin = l_cost - l_count * p_cost
            margin += product_margin
            result += f'''\n    Лот {l_article}: {l_name} ({l_description})
        Цена закупки: {l_cost}₽
        Цена за единицу: {round(l_cost / l_count, 2)}₽
        Запрашиваемое количество: {l_count} шт.,
        Продаваемый товар: {p_article} ({p_name})
        Цена за единицу: {p_cost}₽
        Маржа: {round(product_margin, 2)}₽
        Маржа%: {round(product_margin / l_cost * 100, 2)}%'''
            coverage += l_cost
        result += f'\nОбщая маржа: {round(margin, 2)}₽'
        result += f'\nОбщая маржа%: {round(margin / card_cost * 100, 2)}₽%'
        result += f'\nПокрываемость: {round(coverage / card_cost * 100, 2)}%'
        result += f'\nНе покрытые товары: {"; ".join(other_lots)}\n\n' if other_lots else '\n\n'
        result = result.replace('.00 ', '').replace('.0 ', ' ').replace(';)', ')').replace(' ;', ';')

        update_file(path, result)
        for lot in lots_products:
            set_status('lots', lot[0], 'success')
        set_status('cards', card_id, 'success')
