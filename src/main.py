import os
from datetime import datetime

from __all_func import *
from config import *
from prompts import *


def main():
    prompt_tokens, completion_tokens = 0, 0
    os.mkdir(f'../results/{dir}')

    # категории товаров из файла (вручную) и ключевые (через ИИ по КТ)
    # product_categories = get_text_from_file('../input/product_category.txt')
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
    # category_key_words = dict(list(category_key_words.items())[0:2])

    category_key_words = {'тетрадь': ['тетрадь'], 'блокнот': ['блокнот']}
    key_words = ['тетрадь', 'блокнот']
    # карточки тендеров
    key_word_cards, cards = get_cards(key_words)
    print(f'{datetime.now()}: Собраны все карточки.')
    save_result(f'../results/{dir}/4_cards.txt', '\n'.join([cards[card]['link'] for card in cards]))
    category_cards = {}
    true_cards = []
    for category in category_key_words:
        category_cards_all = [card for word in category_key_words[category] for card in key_word_cards[word]]
        cards_info = '\n'.join(
            [f'{card}: {"; ".join([cards[card]["products"][pr]["name"] for pr in cards[card]["products"]])}' for card in
             category_cards_all if cards[card]['products'] != {}])
        true_cards_answ = make_request_to_ai(prompt_get_cards_1.replace('//Заменить1//', category), cards_info)
        prompt_tokens += true_cards_answ[1]
        completion_tokens += true_cards_answ[2]
        true_cards_answ = [card.strip() for card in true_cards_answ[0].split('\n')]
        for card in true_cards_answ:
            if card in cards:
                true_cards.append(card)
        category_cards[category] = true_cards_answ
    print(f'{datetime.now()}: Отобраны релевантные карточки. Фильтр 1')
    save_result(f'../results/{dir}/5_filter_1.txt', '\n'.join(
        [f"{category}\n{'\n'.join([cards[card]['link'] for card in category_cards[category] if card in cards])}\n" for
         category in category_cards]))
    save_result(f'../results/{dir}/5_filter_1_not_true.txt',
                '\n'.join([cards[card]['link'] for card in cards if card not in true_cards]))

    # парсинг файла
    file_text = get_text_from_file_by_words('../input/Прайс ХАТБЕР 27.08.25 цены С НДС.xlsx', ['тетрадь', 'блокнот']) # product_categories.split('\n')[0:2])
    title = '\n'.join(file_text['title'])
    file_text.pop('title')
    category_products = {}
    products = {}
    for category in file_text:
        file_text[category] = '\n'.join(file_text[category])
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
        if category in category_cards:
            answer = make_request_to_ai(promt_count_margin.replace('//Заменить//','\n'.join([product + ': ' + products[product][0] + '; ' + products[product][1] for product in category_products[category]])),
                                        '\n'.join([card + ': ' + '; '.join([pr + " (" + cards[card]['products'][pr]["name"] + "; " + cards[card]['products'][pr]["description"] + ")" for pr in cards[card]['products']]) for card in category_cards[category]]))
            prompt_tokens += answer[1]
            completion_tokens += answer[2]
            margin_info += answer[0]
    save_result(f'../results/{dir}/9_margin_info.txt', margin_info)
    print(f'{datetime.now()}: Подготовлены данные для подсчета маржи')

    # подсчет маржи
    margin = {}
    for pair in margin_info.strip().replace('\n\n', '\n').split('\n'):
        if len(pair.strip().split(':', 1)) == 2:
            card, their_our = [i.strip() for i in pair.strip().split(':', 1)]
            if ';' in their_our and len(their_our.split(';', 1)) == 2:
                their, our = [i.strip() for i in their_our.split(';', 1)]
                if our in products:
                    if card not in margin:
                        margin[card] = {}
                    margin[card][their] = our
            else:
                print('!----------', their_our)
        else:
            print('!----------', pair)
    result = ''
    for card in margin:
        count_margin, count_coverage = 0, 0
        not_coverage = []
        try:
            result += f'[{cards[card]["name"]}]({cards[card]["link"]})\nОбщая сумма закупки: {cards[card]["cost"]}\nРегион: {cards[card]["region"]}'
            for product in cards[card]['products']:
                if product in margin[card]:
                    product_margin = cards[card]['products'][product]['cost'] - cards[card]['products'][product][
                        'count'] * float(products[margin[card][product]][1])
                    count_margin += product_margin
                    result += f'''\n  Лот {product}: {cards[card]['products'][product]['name']} ({cards[card]['products'][product]['description']})
    Цена закупки: {cards[card]['products'][product]['cost']}₽
    Цена за единицу: {round(cards[card]['products'][product]['cost'] / cards[card]['products'][product]['count'], 2)}₽
    Запрашиваемое количество: {cards[card]['products'][product]['count']} шт.,
    Продаваемый товар: {margin[card][product]} ({products[margin[card][product]][0]})
    Цена за единицу: {products[margin[card][product]][1]}₽
    Маржа: {round(product_margin, 2)}₽
    Маржа%: {round(product_margin / cards[card]['products'][product]['cost'] * 100, 2)}%'''
                    count_coverage += cards[card]['products'][product]['cost']
                else:
                    not_coverage.append(cards[card]['products'][product]['name'] + ' (' + product + ')')
            result += f'\nОбщая маржа: {round(count_margin, 2)}₽'
            result += f'\nОбщая маржа%: {round(count_margin / cards[card]["cost"] * 100, 2)}₽%'
            result += f'\nПокрываемость: {round(count_coverage / cards[card]["cost"] * 100, 2)}%'
            result += f'\nНе покрытые товары: {"; ".join(not_coverage)}\n\n' if not_coverage else '\n\n'
        except Exception as e:
            print(card, margin[card], e)
    result = result.replace('.00 ', '').replace('.0 ', ' ').replace(';)', ')')

    save_result(f'../results/{dir}/10_result.txt', result)
    print(
        f'Общая стоимость: {prompt_tokens / 1000 * COST_INPUT_TOKENS * 81} + {completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81} = {prompt_tokens / 1000 * COST_INPUT_TOKENS * 81 + completion_tokens / 1000 * COST_OUTPUT_TOKENS * 81}')


if __name__ == '__main__':
    dir = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
    for filename in os.listdir('../files'):
        file_path = os.path.join('../files', filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Ошибка при удалении {file_path}: {e}')
    print(f'{datetime.now()}: Запуск')
    main()
