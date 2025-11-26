from pathlib import Path

from .__all_func import *
from .prompts import *


def get_tender_cards(scripts):
    files, costs = [], []
    try:
        for script in scripts:
            cost = 0
            product_categories = get_text_from_file(script[1]).split('\n')
            key_words = get_text_from_file(script[2]).split('\n')
            category_key_words = {}
            for pair in key_words:
                if pair.strip():
                    if len(pair.split(':')) == 2:
                        category, word = [i.strip() for i in pair.split(':', 1)]
                        if category not in category_key_words:
                            category_key_words[category] = []
                        category_key_words[category].append(word)
            # product_categories = ['тетрадь']
            # category_key_words = {'тетрадь': ['тетрадь']}
            cards, urls = get_cards(category_key_words)
            looked_cards = get_text_from_file(script[4]).split('\n')
            not_looked_cards = [card for card in cards if card not in looked_cards]
            if not not_looked_cards:
                continue
            card_lots, lots = get_lots([[card, cards[card]['link']] for card in not_looked_cards])
            category_true_lots = {}
            for category in product_categories:
                category_true_lots[category] = []
                for lot in lots:
                    if category.lower() in lots[lot]["name"].lower():
                        category_true_lots[category].append(lot)
            save_result(script[4], '\n'.join(looked_cards + not_looked_cards))
            products_file = get_text_from_file(script[3]).split('\n')
            products, category_products = {}, {}
            for string in products_file:
                if string.strip():
                    category, article, name, cost = [i.strip() for i in string.split(';')]
                    if category not in category_products:
                        category_products[category] = []
                    category_products[category].append(article)
                    products[article] = [name, cost]
            margin_info = ''
            for category in category_products:
                if category not in category_true_lots or not category_true_lots[category]:
                    continue  # Нет лотов для этой категории

                try:
                    products_text = '\n'.join([f'{product}: {products[product][0]}; {products[product][1]}' for product in category_products[category]])

                    lots_text = '\n'.join([f'{lot}: {lots[lot]['name']} ({lots[lot].get('description', '')})' for lot in category_true_lots[category]])
                    answer = make_request_to_ai(promt_count_margin.replace('//Заменить//', products_text), lots_text)
                    if answer:
                        margin_info += answer[0]
                        prompt_tokens, completion_tokens = answer[1], answer[2]
                        cost += prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81
                except Exception as e:
                    continue

            margin = {}
            if margin_info:
                for pair in margin_info.strip().replace('\n\n', '\n').split('\n'):
                    if len(pair.strip().split(':', 1)) == 2:
                        lot, pr = [i.strip() for i in pair.split(':', 1)]
                        if pr in products:
                            margin[lot] = pr
            for pair in margin_info.strip().replace('\n\n', '\n').split('\n'):
                if len(pair.strip().split(':', 1)) == 2:
                    lot, pr = [i.strip() for i in pair.split(':', 1)]
                    if pr in products:
                        margin[lot] = pr
            result = ''
            for card in not_looked_cards:
                if not any([lot for lot in card_lots[card] if lot in margin]):
                    continue
                count_margin, count_coverage = 0, 0
                not_coverage = []
                result += f'[{cards[card]["name"]}]({cards[card]["link"]})\nОбщая сумма закупки: {cards[card]["cost"]}\nРегион: {cards[card]["region"]}'
                for lot in card_lots[card]:
                    if lot in margin:
                        product_margin = lots[lot]['cost'] - lots[lot]['count'] * float(products[margin[lot]][1])
                        count_margin += product_margin
                        result += f'''\n  Лот {'-'.join(lot.split('-')[1:])}: {lots[lot]['name']} ({lots[lot]['description']})
                Цена закупки: {lots[lot]['cost']}₽
                Цена за единицу: {round(lots[lot]['cost'] / lots[lot]['count'], 2)}₽
                Запрашиваемое количество: {lots[lot]['count']} шт.,
                Продаваемый товар: {margin[lot]} ({products[margin[lot]][0]})
                Цена за единицу: {products[margin[lot]][1]}₽
                Маржа: {round(product_margin, 2)}₽
                Маржа%: {round(product_margin / lots[lot]['cost'] * 100, 2)}%'''
                        count_coverage += lots[lot]['cost']
                    else:
                        not_coverage.append(lot + ' (' + lots[lot]['name'] + ')')
                result += f'\nОбщая маржа: {round(count_margin, 2)}₽'
                result += f'\nОбщая маржа%: {round(count_margin / cards[card]["cost"] * 100, 2)}₽%'
                result += f'\nПокрываемость: {round(count_coverage / cards[card]["cost"] * 100, 2)}%'
                result += f'\nНе покрытые товары: {"; ".join(not_coverage)}\n\n' if not_coverage else '\n\n'
            result = result.replace('.00 ', '').replace('.0 ', ' ').replace(';)', ')')

            project_root = Path(__file__).parent.parent.parent
            path = project_root / 'results' / f'{datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}'
            os.mkdir(path)
            path = f'{path}/{script[0]}.txt'
            save_result(path, result)
            files.append(path)
            costs.append(cost)
        return [files, costs]
    except Exception as e:
        return [[], []]

