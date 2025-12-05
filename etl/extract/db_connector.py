import sqlite3

from config import DB_NAME


def get_scripts(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    scripts = cursor.execute('''SELECT id, name FROM scripts WHERE user_id = ?''', (user_id, )).fetchall()
    connection.close()
    return [[script[0], script[1]] for script in scripts]


def get_users():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    connection.close()
    return [user[0] for user in users]


def get_users_with_access():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users WHERE access = 1''').fetchall()
    connection.close()
    return [user[0] for user in users]


def get_status(table, filed_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    status = cursor.execute(f'''SELECT status FROM {table} WHERE id = ? ''', (filed_id,)).fetchone()
    connection.close()
    return status[0]


def get_keywords(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    keywords = cursor.execute(F'''SELECT name FROM keywords WHERE script_id = ?''', (script_id,)).fetchall()
    connection.close()
    return [keyword[0] for keyword in keywords]


def get_not_looked_cards(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cards = cursor.execute(F'''SELECT number, link FROM cards WHERE script_id = ? AND status = "new" ''', (script_id,)).fetchall()
    connection.close()
    return [[card[0], card[1]] for card in cards]
