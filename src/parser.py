import os

from __all_func import *
from config import *
from prompts import *


prompt_tokens, completion_tokens = 0, 0


def get_categories_key_words(file_name='../input/product_category.txt'):
    global prompt_tokens, completion_tokens
    # # категории товаров из файла (вручную) и ключевые (через ИИ по КТ)
    product_categories = get_text_from_file(file_name)
    print(f'{datetime.now()}: Выделены категории товаров')
    # key_words = make_request_to_ai(prompt_get_key_words, product_categories)
    # prompt_tokens += key_words[1]
    # completion_tokens += key_words[2]
    # category_key_words = {}
    # for pair in key_words[0].strip().split('\n'):
    #     if len(pair.split(':')) == 2:
    #         category, word = [i.strip() for i in pair.split(':', 1)]
    #         if category not in category_key_words:
    #             category_key_words[category] = []
    #         category_key_words[category].append(word)
    # key_words = [word for category in category_key_words for word in category_key_words[category]]
    # save_result(f'../results/{dir}/key_words.txt', '\n'.join(key_words))
    # save_result(f'../results/{dir}/key_word_categories.txt', '\n'.join([f"{category}: {', '.join(category_key_words[category])}" for category in category_key_words]))
    # print(f'{datetime.now()}: Выделены ключевые слова')
    # category_key_words = dict(list(category_key_words.items()))

    product_categories = product_categories.split('\n')
    product_categories = ['тетрадь']
    category_key_words = {'тетрадь': ['тетрадь']} #, 'блокнот': ['блокнот']} #, 'ручки': ['ручки']}
    return product_categories, category_key_words


def filter_lots(category_lots, lots):
    global prompt_tokens, completion_tokens
    category_true_lots = {}
    for category in category_lots:
        category_lots_all = [f'{lot}: {lots[lot]["name"]}' for lot in category_lots[category]]
        if not category_lots_all:
            continue
        lots_info = '\n'.join([f'{lot}: {lots[lot]["name"]}' for lot in category_lots[category]])
        true_lots_answ = make_request_to_ai(prompt_filter.replace('//Заменить1//', category), lots_info)
        prompt_tokens += true_lots_answ[1]
        completion_tokens += true_lots_answ[2]
        category_true_lots[category] = [lot.strip() for lot in true_lots_answ[0].split('\n') if lot.strip() in lots]
    print(f'{datetime.now()}: Отобраны релевантные для каждой категории лоты. Фильтр 1')
    return category_true_lots


def main():
    global prompt_tokens, completion_tokens
    os.mkdir(f'../results/{dir}')

    # категории наших товаров, категории и относящиеся к ни ключевые слова, ключевые слова
    product_categories, category_key_words = get_categories_key_words()

    # карточки тендеров
    category_lots, cards, card_lots, lots, urls = get_cards(category_key_words)
    save_result(f'../results/{dir}/3_searching_links.txt', '\n'.join(urls))
    print(f'{datetime.now()}: Собраны все карточки.')
    save_result(f'../results/{dir}/4_cards.txt', '\n'.join(['; '.join([str(cards[card][i]) for i in cards[card]]) for card in cards]))

    category_true_lots = filter_lots(category_lots, lots)

    lot_card = {}
    for card in card_lots:
        for lot in card_lots[card]:
            lot_card[lot] = card
    save_result(f'../results/{dir}/5_filter_1.txt', '\n'.join(
        [category + '\n' + '\n'.join([f"{lot_card[lot]}: {lot} {lots[lot]["name"]}" for lot in category_true_lots[category]]) + '\n' for category in category_lots]))
    save_result(f'../results/{dir}/5_filter_1_not_true.txt', '\n'.join(
        [category + '\n' + '\n'.join([f"{lot_card[lot]}: {lot} {lots[lot]["name"]}" for lot in category_lots[category] if lot not in category_true_lots[category]]) + '\n' for category in category_lots]))

    # парсинг файла
    file_text = get_text_from_file_by_words('../input/Прайс ХАТБЕР 27.08.25 цены С НДС.xlsx',  product_categories[0:2])
    title = '\n'.join(file_text['title'])
    file_text.pop('title')
    category_products = {}
    products = {}
    for category in file_text:
        answer = make_request_to_ai(prompt_get_key_info_our_products + title, file_text[category])
        prompt_tokens += answer[1]
        completion_tokens += answer[2]
        category_products[category] = []
        for product in answer[0].strip().replace('\n\n', '\n').split('\n'):
            if len(product.strip().split(':', 1)) == 2:
                article, name_cost = [i.strip() for i in product.strip().split(':', 1)]
                if len(name_cost.split(';', 1)) == 2:
                    name, cost = [i.strip() for i in name_cost.split(';', 1)]
                    category_products[category].append(article)
                    products[article] = [name, cost]
    save_result(f'../results/{dir}/8_products.txt', '\n\n'.join([category + '\n' + '\n'.join([product + ': ' + products[product][0] + '; ' + products[product][1] for product in category_products[category]]) for category in category_products]))

    margin_info = ''
    for category in category_products:
        answer = make_request_to_ai(promt_count_margin.replace('//Заменить//','\n'.join([product + ': ' + products[product][0] + '; ' + products[product][1] for product in category_products[category]])),
                                    '\n'.join([f"{lot}: {lots[lot]["name"]} ({lots[lot]["description"]})" for lot in category_true_lots[category]]))
        prompt_tokens += answer[1]
        completion_tokens += answer[2]
        margin_info += answer[0]
    save_result(f'../results/{dir}/9_margin_info.txt', margin_info)
    print(f'{datetime.now()}: Подготовлены данные для подсчета маржи')

    # подсчет маржи
    margin = {}
    for pair in margin_info.strip().replace('\n\n', '\n').split('\n'):
        if len(pair.strip().split(':', 1)) == 2:
            lot, pr = [i.strip() for i in pair.split(':', 1)]
            if pr in products:
                margin[lot] = pr
        else:
            print('!----------', pair)

    result = ''
    for card in cards:
        if not any([lot for lot in card_lots[card] if lot in margin]):
            continue
        count_margin, count_coverage = 0, 0
        not_coverage = []
        # try:
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
        # except Exception as e:
        #     print(card, margin[card], e)
    result = result.replace('.00 ', '').replace('.0 ', ' ').replace(';)', ')')

    save_result(f'../results/{dir}/10_result.txt', result)
    print(f'Общая стоимость: {prompt_tokens / 1000 * COST_INPUT_TOKENS * 81} + {completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81} = {prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81}')


if __name__ == '__main__':
    dir = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
    print(f'{datetime.now()}: Запуск')
    main()
