import datetime
import sqlite3

from config import DB_NAME, ADMIN
from db.db_models.db_connector import get_users


def add_new_user(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    if (user_id, ) not in users:
        cursor.execute('''INSERT INTO users (id, role, access) VALUES (?, ?, ?)''', (user_id, 2, 2))
        connection.commit()
    connection.close()


def change_access(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''UPDATE users SET access = 1 WHERE id = ?''', (user_id,))
    connection.commit()
    connection.close()


def add_new_script(name, user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    new_script = cursor.execute('''INSERT INTO scripts (name, user_id, created_at, status) VALUES (?, ?, ?, ?) RETURNING id''', (name, user_id, datetime.datetime.utcnow(), 'new')).fetchone()
    connection.commit()
    connection.close()
    return new_script[0]


def add_categories(script_id, categories):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    categories_name_id = {}
    for category in categories:
        new_category = cursor.execute('''INSERT INTO categories (name, script_id) VALUES (?, ?) RETURNING id''', (category, script_id)).fetchone()
        categories_name_id[category] = new_category[0]
    connection.commit()
    connection.close()
    return categories_name_id


def add_key_words(script_id, keywords, categories_name_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    for keyword in keywords:
        if keyword.strip():
            category, word = [i.strip() for i in keyword.split(':', 1)]
            if category in categories_name_id:
                cursor.execute('''INSERT INTO keywords (name, category_id, script_id) VALUES (?, ?, ?)''', (word, categories_name_id[category], script_id))
    connection.commit()
    connection.close()


def add_products(script_id, products, category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    for product in products:
        if product.strip():
            if len(product.strip().split(':', 1)) == 2:
                article, name_cost = [i.strip() for i in product.strip().split(':', 1)]
                if len(name_cost.split(';', 1)) == 2:
                    name, cost = [i.strip() for i in name_cost.split(';', 1)]
                    cursor.execute('''INSERT INTO products (article, name, cost, category_id, script_id) VALUES (?, ?, ?, ?, ?)''',
                                   (article, name, float(cost), category_id, script_id))
    connection.commit()
    connection.close()


def set_admins():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    for user_id in ADMIN:
        if user_id not in get_users():
            cursor.execute('''INSERT INTO users (id, role, access) VALUES (?, ?, ?)''', (user_id, 1, 1))
        else:
            cursor.execute('''UPDATE users SET role = 1 WHERE id = ?''', (user_id,))
    connection.commit()
    connection.close()
