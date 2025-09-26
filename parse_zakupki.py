import requests
from bs4 import BeautifulSoup

from datetime import date, datetime
import tiktoken

from config import *
from prompts import *


def get_text_from_file(file_name='ПРАЙС РДК ИЮЛЬ ОПТ СО СКИДКОЙ.pdf'):
    try:
        extension = file_name.split('.')[-1].lower()
        file_text = ''
        if extension == 'pdf':
            import PyPDF2

            with open(file_name, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(reader.pages):
                    file_text += page.extract_text() + '\n'

            return file_text

        elif extension == 'xlsx':
            from openpyxl import load_workbook
            from openpyxl.utils import get_column_letter
            from openpyxl.styles.numbers import BUILTIN_FORMATS

            wb = load_workbook(file_name, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value is not None and cell.value != 0:
                        if isinstance(cell.value, (int, float)):
                            fmt = cell.number_format
                            try:
                                file_text += str(cell.value)  if fmt == 'General' else format(cell.value, '.2f') + ' '
                            except:
                                file_text += str(cell.value) + ' '
                        else:
                            file_text += str(cell.value) + ' '
                file_text += '\n'
        while '\n\n' in file_text:
            file_text = file_text.replace('\n\n', '\n')
        return file_text
    except Exception as e:
        print(f'Ошибка при чтении файла\n{e}')


# def get_key_words(file_text):
    # file_name = 'key_words.txt'
    # with open(file_name, encoding='utf-8') as file:
    #     key_words = [i.strip() for i in file.readlines()]
    # return key_words


def get_date(period=6):
    today = date.today()
    month = today.month - 1 + period
    year = today.year + month // 12
    month = month % 12 + 1
    day = min(today.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    end = date(year, month, day)
    return [today.strftime('%d.%m.%Y'), end.strftime('%d.%m.%Y')]


def get_url(start_date, end_date):
    morphology = ['&morphology=on', ''][0]
    page_number = ['&pageNumber=1', ''][0]  # ?????????????????????????????
    search_filter = ['&search-filter=Дате+размещения', '']  # ????????????? как будто бесполезно из-за sortBy
    sort_direction = '&sortDirection=' + ['false', 'true'][0]  # убывание/возрастание
    records_per_page = '&recordsPerPage=_' + ['10', '20', '50'][0]
    show_lots_info_hidden = '&showLotsInfoHidden=' + ['false', 'true'][0]
    sort_by = '&sortBy=' + ['UPDATE_DATE', 'PUBLISH_DATE', 'PRICE', 'RELEVANCE'][0]
    zakon = ''.join(['&fz44=on', '&fz223=on', '&ppRf615=on', ''])
    stage = ''.join(['&af=on', '&ca=on', '&pc=on', '&pa=on',
                     ''])  # Подача заявок/Работа комиссии/Закупка завершена/Закупка отменена
    currency_id_general = '-1'  # ???????????????????????????????????????
    publish_date_from = ['&publishDateFrom=' + start_date, ''][1]
    publish_date_to = ['&publishDateTo=' + start_date, ''][1]
    appl_submission_close_date_from = ['&applSubmissionCloseDateFrom=' + start_date, ''][0]
    appl_submission_close_date_to = ['&applSubmissionCloseDateTo=' + end_date, ''][0]

    url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={morphology}{zakon}{stage}{appl_submission_close_date_from}{appl_submission_close_date_to}'
    return url


def make_request_to_ai(text, model=MODEL):
    try:
        headers = {
            'Authorization': f'Bearer {AI_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': text}, ]
        }

        response = requests.post(AI_URL, headers=headers, json=data)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f'Ошибка в отправке запроса модели\n{e}')


def save_result(file_name, *result, mode='w'):
    try:
        if mode == 'wb':
            with open(file_name, mode='wb') as file:
                for i in result.iter_content(chunk_size=8192):
                    print(i, '\n\n\n\n------------------------------------------------------\n\n\n')
                    file.write(i)
        else:
            with open(file_name, encoding='utf-8', mode='w') as file:
                file.write('\n'.join(result))
        print(f'Результат сохранен в файл {file_name}')
    except Exception as e:
        print(f'Ошибка при сохранении результата в файл\n{e}')


def less_max_tokens(prompt, full_text, model=MODEL):
    def count_tokens(text):
        if 'gpt' in model:
            enc = tiktoken.encoding_for_model(model)
            tokens = enc.encode(prompt + text)
        elif 'Qwen' in model:
            try:
                from transformers import AutoTokenizer
                tokenizer  = AutoTokenizer.from_pretrained(model)
                tokens = tokenizer.encode(prompt + text)
            except Exception as e:
                print(f'Ошибка при подсчете токенов\n{e}')
        return tokens

    tokens_full_text = len(count_tokens(full_text))
    tokens_prompt = len(count_tokens(prompt))
    # print(f'Количество токенов: {tokens_prompt + tokens_full_text}')
    if tokens_full_text + tokens_prompt > MAX_TOKENS:
        max_tokens_text = (MAX_TOKENS - tokens_prompt)
        count = tokens_full_text // max_tokens_text + 1
        full_text = [prompt + full_text[i * max_tokens_text:i * max_tokens_text + MAX_TOKENS] for i in range(0, count)]
    else:
        full_text = [prompt + full_text]
    return full_text


def main():
    # key_words = get_key_words()[:7]
    file_text = get_text_from_file('ПРАЙС РДК ИЮЛЬ ОПТ СО СКИДКОЙ.xlsx')
    tokens_file_text = less_max_tokens(promt_get_key_words, file_text, MODEL)

    key_words_answ = []
    for i in tokens_file_text:
        key_words_answ.append(make_request_to_ai(i))
        print(f'{datetime.now()}: Обработка файла: {len(key_words_answ)}/{len(tokens_file_text)}')
    key_words_answ = '\n'.join(key_words_answ)
    # save_result('key_words_ai.txt', key_words_answ)
    key_words = key_words_answ.split('\n')
    print(f'{datetime.now()}: Выделены ключевые слова')

    start_date, end_date = get_date()
    url = get_url(start_date, end_date)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64',
               'Authorization': f'Bearer {ZAKUPKI_TOKEN}',
               'Content-Type': 'application/json'}

    cards = {}
    docs = {}
    for word in key_words[0:7]:
        url_word = url.replace('searchString=&', f'searchString={word.strip()}&')
        response_word = requests.get(url_word, headers=headers)
        soup_word = BeautifulSoup(response_word.text, 'html.parser')
        blocks = soup_word.find_all('div', class_='row no-gutters registry-entry__form mr-0')

        for i in blocks:
            number = i.find('div', class_='registry-entry__header-mid__number').get_text().strip().replace('№ ', '')
            name = i.find('div', class_='registry-entry__body-value').get_text().strip()
            cost = i.find('div', class_='price-block__value').get_text().strip()
            link_on_docs = f'https://zakupki.gov.ru{i.find('div', class_='href d-flex').find('a').get('href')}'
            response_docs = requests.get(link_on_docs, headers=headers)
            soup_docs = BeautifulSoup(response_docs.text, 'html.parser')
            cards[number] = [name, cost, link_on_docs]
            try:
                if 'noticeInfoId' in link_on_docs:
                    docs_names_block = soup_docs.find('div', class_='row pl-3').find_all('span', class_='count')
                    docs_names = [['https://zakupki.gov.ru' + j.find_all('a')[1].get('href'),  j.find_all('a')[1].get_text().strip()] for j in docs_names_block]
                elif 'regNumber' in link_on_docs:
                    docs_names_block = soup_docs.find('div', class_='blockFilesTabDocs').find_all('span', class_='section__value')
                    docs_names = [['https://zakupki.gov.ru' + j.find('a').get('href'), j.find('a').get_text().strip()] for j in docs_names_block]
                for i in docs_names:
                    docs[i[1]] = i[0]
                    cards[number].append(i[1])
            except Exception as e:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', link_on_docs, e, response_docs.text)
                cards[number].append(' ')

    print(f'{datetime.now()}: Собраны все карточки.')
    save_result('key_words_cards.txt', key_words_answ, '\n'.join([cards[i][2] for i in cards]))

    cards_info = '\n'.join([f'{i}: {cards[i][0]} Документы: {', '.join(cards[i][3:])}' for i in cards])
    tokens_cards = less_max_tokens(promt_get_cards.replace('//Заменить1//', key_words_answ.replace('\n', ', ')), cards_info)
    true_cards_answ = []
    for i in tokens_cards:
        true_cards_answ.append(make_request_to_ai(i))
        print(f'{datetime.now()}: Обработка файла: {len(true_cards_answ)}/{len(tokens_cards)}')

    true_cards_answ = '\n'.join(true_cards_answ).split('\n')
    print(cards)
    true_cards = {}
    for i in true_cards_answ[0:5]:
        try:
            card_num, doc_name = [j.strip() for j in i.strip().split(':')]
            if doc_name not in docs:
                for j in cards[card_num][3:]:
                    if doc_name in j:
                        doc_link = j
            else:
                doc_link = docs[doc_name]
            true_cards[card_num] = cards[card_num][:3] + [doc_link]
        except Exception as e:
            print('-------------------', doc_name, cards[card_num])
    print(f'{datetime.now()}: Отобраны релевантные карточки.')
    print(true_cards)

    # for card in true_cards:
    #     response_docs = requests.get(true_cards[card][2], headers=headers)
    #     soup_docs = BeautifulSoup(response_docs.text, 'html.parser')
    #     docs_name = soup_docs.find('div', class_='row pl-3').find('div', class_='attachment__value').find('span')
    #     print(true_cards[card][2], docs_name)
    #
    #     true_cards[card].append(docs_name)

    true_cards_info = '\n'.join([f'{i}: {true_cards[i]}' for i in true_cards])

    answer = make_request_to_ai(promt_count_margin.replace('//Заменить1//', file_text).replace('//Заменить2//', true_cards_info), '')
    print(f'{datetime.now()}: Подсчитана маржа')
    save_result('result.txt', answer)

if __name__ == '__main__':
    main()
    # get_text_from_file('ПРАЙС РДК ИЮЛЬ ОПТ СО СКИДКОЙ.xlsx')
    # print(make_request_to_ai(f'Почему токенов в первом случае больше чем во втором, покажи различия в тексте. В первом случае excel файл парсился с помощью openpyxl, во втором случае сначала преобразован в pdf, потом парсился с помощью pypdf2. Первый случай: {get_text_from_file('ПРАЙС РДК ИЮЛЬ ОПТ СО СКИДКОЙ.xlsx')} Второй случай: {get_text_from_file()}'))
