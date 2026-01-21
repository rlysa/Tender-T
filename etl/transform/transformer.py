import re

from config import COST_INPUT_TOKENS, COST_OUTPUT_TOKENS
from etl.extract.db_connector import *
from etl.load.loader import *
from services.ai_service import make_request_to_ai
from services.prompts import prompt_count_margin, prompt_get_struct_info_lots
from utils.files import update_file
from db.db_models.db_connector import get_template_category, get_cost_script
from db.db_models.loader import update_cost_script


def filter_lots(script_id):
    lots = get_not_filtered_lots(script_id)
    categories = get_categories(script_id)
    for category in categories:
        for lot in lots:
            if any(word.lower() in lot[1].lower() for word in category[1].split(' ')):
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


def correct_lots_description(script_id):
    for category in get_categories(script_id):
        temp = get_template_category(category[0])
        lots = get_filtered_lots(script_id, category[0])
        lots = [lots[i:i + 100] for i in range(0, len(lots), 100)]

        for nlot in lots:
            answer = make_request_to_ai(prompt_get_struct_info_lots.replace('//Заменить1//', str(len(nlot))).replace('//Заменить2//', temp),
                                        '\n'.join(nlot))
            if not answer or len(answer) < 3:
                return
            prompt_tokens, completion_tokens = answer[1], answer[2]
            cost = get_cost_script(script_id)
            cur_cost = prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            update_cost_script(script_id, cost)
            update_lots(answer[0].strip().split('\n'), temp)
    set_status('scripts', script_id, 'match')


def match_products_lots(script_id):
    categories = get_categories(script_id)
    for category in categories:
        products = get_products(script_id, category[0])
        lots = get_described_lots(script_id, category[0])
        for lot in lots:
            lot_desc = ':'.join([i.split(':')[1].strip() for i in lot[2].lower().split(';')])
            prod = []
            for product in products:
                pr_desc = ':'.join([i.split(':')[1].strip() for i in product[2].lower().split(';')])
                if strings_match(pr_desc, lot_desc) and product[-1]:
                    prod.append(product)
            answer = make_request_to_ai(prompt_count_margin.replace('//Заменить//', f'{lot[0]}: {lot[1]}'), '\n'.join([f'{pr[0]}: {pr[1]} {pr[2]}' for pr in prod]))
            prompt_tokens, completion_tokens = answer[1], answer[2]
            cur_cost = prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
            cost = get_cost_script(script_id)
            update_cost_script(script_id, round(cur_cost + cost, 2))
            not_relevant = [pr.strip() for pr in answer[0].split('\n')]
            prod = [pr for pr in prod if pr[0] not in not_relevant]
            if prod != []:
                prod = sorted(prod, key=lambda x: x[-1] if x[-1] else 0)
                set_match_product(lot[0], prod[0][0])
                set_status('lots', lot[0], 'matched')


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


def strings_match(str1, str2, threshold=0.5):
    # Разбиваем строки на значения
    items1 = [item.strip() for item in str1.split(';')]
    items2 = [item.strip() for item in str2.split(';')]

    # Выравниваем по длине
    min_len = min(len(items1), len(items2))
    items1, items2 = items1[:min_len], items2[:min_len]

    matches = 0
    relevant_items = 0

    for val1, val2 in zip(items1, items2):
        # Если во второй строке "-" - пропускаем (не важно)
        if val2 == '-':
            continue

        relevant_items += 1

        # Если в первой строке "-" - не совпадает
        if val1 == '-':
            continue

        # Пытаемся найти числа в значениях
        num_match1 = re.search(r'\d+', val1)
        num_match2 = re.search(r'\d+', val2)

        if num_match1 and num_match2:
            n1 = int(num_match1.group())
            n2 = int(num_match2.group())

            # Ищем операторы сравнения во втором значении
            if '>=' in val2:
                if n1 >= n2:
                    matches += 1
            elif '>' in val2:
                if n1 > n2:
                    matches += 1
            elif '<=' in val2:
                if n1 <= n2:
                    matches += 1
            elif '<' in val2:
                if n1 < n2:
                    matches += 1
            elif '=' in val2:
                if n1 == n2:
                    matches += 1
            else:
                # Просто числа
                if n1 == n2:
                    matches += 1
        else:
            # Сравниваем текстовые значения (регистронезависимо)
            if val1.lower() == val2.lower():
                matches += 1
            # Если значения похожи (на скобе vs скрепки) - считаем совпадением
            elif ('скоб' in val1.lower() and 'скреп' in val2.lower()) or \
                    ('скреп' in val1.lower() and 'скоб' in val2.lower()):
                matches += 1

    if relevant_items == 0:
        return True

    return matches / relevant_items >= threshold