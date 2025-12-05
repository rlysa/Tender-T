import datetime
import sqlite3

from config import DB_NAME


def set_status(table, field, field_id, status, inf=''):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(f'''UPDATE {table} SET status = ? WHERE {field} = ? {inf}''', (status, field_id))
    connection.commit()
    connection.close()


def add_card(number, name, cost, link, script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    processed_cards = cursor.execute('''SELECT number FROM cards WHERE script_id = ? ''', (script_id,)).fetchall()
    if (number, ) not in processed_cards:
        cursor.execute('''INSERT INTO cards (number, name, cost, link, extracted_at, script_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (number, name, cost, link,  datetime.datetime.utcnow(), script_id, 'new'))
        connection.commit()
    connection.close()


def set_region(card_id, region, script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''UPDATE cards SET region = ? WHERE number = ? AND script_id = ? ''', (region, card_id, script_id))
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
