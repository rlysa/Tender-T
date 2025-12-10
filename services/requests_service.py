import requests
from bs4 import BeautifulSoup
import time

from config import ZAKUPKI_TOKEN


def make_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
               'Authorization': f'Bearer {ZAKUPKI_TOKEN}',
               'Content-Type': 'application/json'}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                if any(text in response.text.lower() for text in ['captcha', 'blocked', 'доступ запрещен']):
                    time.sleep(10 * (attempt + 1))
                    continue

                return soup

            elif response.status_code == 429:
                wait_time = 30 * (attempt + 1)
                time.sleep(wait_time)

            else:
                time.sleep(5)

        except requests.exceptions.RequestException as e:
            time.sleep(5 * (attempt + 1))

        except Exception as e:
            time.sleep(5)

    return None