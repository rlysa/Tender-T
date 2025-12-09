import re
import time
from datetime import date

from services.requests_service import make_request
from etl.load.loader import *
from etl.extract.db_connector import *


def get_cards(script_id):
    try:
        start_date, end_date = get_date()
        url = get_url(start_date, end_date)
        words = get_keywords(script_id)
        for index, word in enumerate(words):
            time.sleep(1)
            url_word = url.replace('searchString=&', f'searchString={word.strip()}&')
            soup_word = make_request(url_word)
            if not soup_word:
                continue
            total = soup_word.find('div', class_='search-results__total').get_text()
            total = int(''.join([i for i in total if i.isdigit()]))
            pages = total // 50 + 1 if total > 50 else 1
            blocks = soup_word.find_all('div', class_='row no-gutters registry-entry__form mr-0')
            if pages > 1:
                for i in range(2, pages + 1):
                    time.sleep(1)
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

                add_card(number, name, cost, link, script_id)
    except Exception as e:
        raise Exception(f'Ошибка при поиске карточек {e}')


def get_lots(script_id):
    try:
        cards = get_not_looked_cards(script_id)
        for index, card in enumerate(cards):
            card_id, number, link = card
            soup_info = make_request(link)
            region = soup_info.find('span', class_='section__title', string='Регион')
            region = region.find_next('span', class_='section__info').get_text(strip=True) if region else ''
            set_region(card_id, region)

            info = soup_info.find('div', class_='container', id='positionKTRU')
            if not info:
                set_status('cards', card_id, 'finished')
            else:
                lots = {}
                table = info.find('div', id=re.compile(r'purchaseObjectTruTable\d+'))
                if not table:
                    set_status('cards', card_id, 'finished')
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
                        if article in lots:
                            article += f'-1'
                            while article in lots:
                                article = '-'.join(article.split('-')[0:2]) + '-' + str(int(article.split('-')[-1]) + 1)
                        lots[article] = {'name': pr_name.strip(),
                                         'description': description.strip(),
                                         'count': float(re.sub(r'\xa0', '', count).replace(',', '.')),
                                         'cost': float(re.sub(r'\xa0', '', cost_pr.replace(',', '.')))}
                    except Exception as e:
                        raise Exception(f'Ошибка получении информации лотов {e}')
                for lot in lots:
                    add_lot(lot, lots[lot]['name'], lots[lot]['description'], lots[lot]['count'], lots[lot]['cost'], card_id)
            set_status('cards', card_id, 'get_lots')
    except Exception as e:
        raise Exception(f'Ошибка при поиске лотов {e}')


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