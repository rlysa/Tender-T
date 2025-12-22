from datetime import datetime
import sqlite3
from zoneinfo import ZoneInfo

from config import DB_NAME


def set_status(table, id_value, status):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE {table} SET status = ? WHERE id = ? ''', (status, id_value))
    connection.commit()
    connection.close()


def add_card(number, name, cost, link, script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    processed_cards = cursor.execute('''SELECT number FROM cards WHERE script_id = ? ''', (script_id,)).fetchall()
    if (number, ) not in processed_cards:
        cursor.execute('''INSERT INTO cards (number, name, cost, link, extracted_at, script_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (number, name, cost, link,  datetime.now(ZoneInfo("Europe/Moscow")), script_id, 'new'))
        connection.commit()
    connection.close()


def set_region(card_id, region):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''UPDATE cards SET region = ? WHERE id = ? ''', (region, card_id))
    connection.commit()
    connection.close()


def add_lot(article, name, description, count, cost, card_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    processed_lots = cursor.execute('''SELECT article FROM lots WHERE card_id = ? ''', (card_id,)).fetchall()
    if (article,) not in processed_lots:
        cursor.execute(
            '''INSERT INTO lots (article, name, description, count, cost, card_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (article, name, description, count, cost, card_id, 'new'))
        connection.commit()
    connection.close()


def set_category(lot_id, category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE lots SET category_id = ? , status = "filtered" WHERE id = ? ''', (category_id, lot_id))
    connection.commit()
    connection.close()


def set_relevant(card_id, relevant):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE cards SET relevant = ? WHERE id = ? ''', (relevant, card_id))
    connection.commit()
    connection.close()


def set_match_product(lot_id, product_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE lots SET match_product_id = ? , status = "matched" WHERE id = ? ''', (product_id, lot_id))
    connection.commit()
    connection.close()


def set_finish_status(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE lots SET status = "finished" WHERE status = "success" ''')
    cursor.execute(f'''UPDATE cards SET status = "finished" WHERE script_id = ? AND status = "success" ''', (script_id, ))
    connection.commit()
    connection.close()
