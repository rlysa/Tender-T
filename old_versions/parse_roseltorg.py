import requests
from bs4 import BeautifulSoup
from datetime import date

def get_key_words(file_name='key_words.txt'):
    with open(file_name, encoding='utf-8') as file:
        key_words = [i.strip() for i in file.readlines()]
    return key_words


def get_date(period=6):
    today = date.today()
    month = today.month - 1 + period
    year = today.year + month // 12
    month = month % 12 + 1
    day = min(today.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    end = date(year, month, day)
    return [today.strftime('%d.%m.%y'), end.strftime('%d.%m.%y')]


def main(status_torgov=None):
    key_words = get_key_words()
    key_words_links = {i: [] for i in key_words}
    print(key_words_links)

    filter_status = [0, 1, 2, 3, 4, 5] # ['Прием заявок', 'Работа комиссии', 'Процедура отменена', 'Приостановлена', 'Процедура завершена', 'Ожидание приема заявок']
    filter_currency = 4 # ['0', 'RUB', 'USD', 'EUR', 'all']
    filter_way = [21, 1, 2, 3, 4, 5] # ['Продажа посредством публичного предложения' - 21, 'Аукцион на повышение', 'Аукцион на понижение', 'Конкурс', 'Запрос предложений', 'Запрос котировок']

    status = '&'.join([f'status%5B%5D={istatus}' for istatus in filter_status])
    currency = filter_currency
    start_date, end_date = get_date()
    start_date_requests = 'start_date_requests' + start_date
    end_date_requests = 'end_date_requests' + end_date
    type_t = '&'.join([f'type%5B%5D={iway}' for iway in filter_way])
    url = f'https://www.roseltorg.ru/procedures/search?sale=1&query_field=&{status}&{currency}&{type_t}&{start_date_requests}&{end_date_requests}'.replace('&&', '&')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64'}

    links = []
    for word in key_words[0:1]:
        url_word = url.replace('query_field=&', f'query_field={word}&')
        response = requests.get(url_word, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup.prettify())
        links = soup.find_all('div', class_='search-results__item autoload-post')
        for i in links:
            print(f"{i.attrs['data-feature-favorite-lots-procedure-number']}_{i.attrs['data-feature-favorite-lots-lot-number']}")
        print(*links, sep='\n\n-------------------------------------------\n\n')



if __name__ == '__main__':
    main()
