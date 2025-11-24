import requests
import re
from bs4 import BeautifulSoup
import time
from datetime import datetime, date

from config import *


def make_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
               'Authorization': f'Bearer {ZAKUPKI_TOKEN}',
               'Content-Type': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        soup = None
        while not soup:
            while response.status_code != 200 or 'connection aborted' in response.text.lower():
                time.sleep(2)
                print(f'{datetime.now()}: Переподключение')
                response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
    except Exception as e:
        print(requests.get(url, headers=headers).status_code, e)


def get_cards(words):
    cards, urls = {}, []
    start_date, end_date = get_date()
    url = get_url(start_date, end_date)

    print(f'{datetime.now()}: Поиск карточек:{len(words)}')
    for index, word in enumerate(words):
        url_word = url.replace('searchString=&', f'searchString={word.strip()}&')
        urls.append(url_word)
        soup_word = make_request(url_word)
        total = soup_word.find('div', class_='search-results__total').get_text()
        total = int(''.join([i for i in total if i.isdigit()]))
        pages = total // 50 + 1 if total > 50 else 1
        blocks = soup_word.find_all('div', class_='row no-gutters registry-entry__form mr-0')
        if pages > 1:
            for i in range(2, pages + 1):
                soup_pages = make_request(f'{url_word}&pageNumber={i}')
                blocks += soup_pages.find_all('div', class_='row no-gutters registry-entry__form mr-0')
        for i, block in enumerate(blocks):
            number = block.find('div', class_='registry-entry__header-mid__number').get_text().strip().replace('№ ', '')
            name = block.find('div', class_='registry-entry__body-value').get_text().strip()
            cost = block.find('div', class_='price-block__value')
            if not cost:
                continue
            cost = cost.get_text().strip().split(' ')[0].strip()
            cost = float(re.sub(r'\xa0', '', cost).replace(',', '.'))
            link = f'https://zakupki.gov.ru{block.find('div', class_='registry-entry__header-mid__number').find('a').get('href')}'
            links = ['https://zakupki.gov.ru/epz/order/notice/zk20/view/common-info.html?regNumber=0112200000825004885',
                     'https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0865200000325001444',
                     'https://zakupki.gov.ru/epz/order/notice/zk20/view/common-info.html?regNumber=0340100009725000079']
            # if link not in links:
            #     continue
            link_on_docs = f'https://zakupki.gov.ru{block.find('div', class_='href d-flex').find('a').get('href')}'
            soup_info = make_request(link)
            region = soup_info.find('span', class_='section__title', string='Регион')
            region = region.find_next('span', class_='section__info').get_text(strip=True) if region else ''
            cards[number] = {'name': name, 'region': region, 'cost': cost, 'link': link, 'link_on_docs': link_on_docs}
    return [cards, urls]


def get_lots(cards):
    lots, card_lots = {}, {}
    print(f'{datetime.now()}: Сбор лотов: {len(cards)}')
    for index, card in enumerate(cards):
        number, link = card
        soup_info = make_request(link)
        info = soup_info.find('div', class_='container', id='positionKTRU')
        card_lots[number] = []
        if not info:
            link_on_lots = soup_info.find('div', class_='tabsNav d-flex')
            if 'Список лотов' in link_on_lots.get_text():
                print(link, 'lots')
            else:
                print(link, 'docs')
        else:
            table = info.find('div', id=re.compile(r'purchaseObjectTruTable\d+'))
            if not table:
                continue
            rows = table.find_all('tr', class_='tableBlock__row')
            for row in rows:
                try:
                    if 'truInfo_' in str(row.get('class', [])) or row.find('th'):
                        continue
                    chevron = row.find('span', class_='chevronRight')
                    if not chevron:
                        continue
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 7:
                        continue
                    article = cells[1].get_text().strip().split()
                    if len(article) == 2:
                        article = article[1]
                    else:
                        article = article[0] + '-00000000'
                    pr_name = cells[2].get_text().strip().split('\n')[0]
                    count = cells[-3].get_text(strip=True)
                    if count == '':
                        count = '1'
                    cost_pr = cells[-1].get_text(strip=True)
                    description = ''
                    row_id = chevron.get('onclick', '')
                    if 'showInfo' in row_id:
                        match = re.search(r"showInfo\('([^']+)'", row_id)
                        if match:
                            hidden_section_id = match.group(1)
                            hidden_section = info.find('tr', class_=hidden_section_id)
                            if hidden_section:
                                char_table = hidden_section.find('table', class_='tableBlock')
                                if char_table:
                                    char_rows = char_table.find_all('tr', class_='tableBlock__row')
                                    for char_row in char_rows[1:]:
                                        char_cells = char_row.find_all(['td', 'th'])
                                        if len(char_cells) >= 4:
                                            char_name = char_cells[0].get_text(strip=True)
                                            char_value = char_cells[1].get_text(strip=True)
                                            char_unit = char_cells[2].get_text(strip=True)
                                            if char_name and char_value:
                                                if char_unit:
                                                    description += f'{char_name}: {char_value} {char_unit}; '
                                                else:
                                                    description += f'{char_name}: {char_value}; '
                    article = f'{number}-{article}'
                    if article in lots:
                        article += f'-1'
                        while article in lots:
                            article = '-'.join(article.split('-')[:-1]) + '-' + str(int(article.split('-')[-1]) + 1)
                    lots[article] = {'name': pr_name,
                                     'description': description.strip(),
                                     'count': float(re.sub(r'\xa0', '', count).replace(',', '.')),
                                     'cost': float(re.sub(r'\xa0', '', cost_pr.replace(',', '.')))}
                    card_lots[number].append(article)
                except Exception as e:
                    print('!----------', link, e)
    return [card_lots, lots]


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
    records_per_page = '&recordsPerPage=_' + ['10', '20', '50'][2]
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

    url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={morphology}{zakon}{stage}{appl_submission_close_date_from}{appl_submission_close_date_to}{records_per_page}'
    return url
