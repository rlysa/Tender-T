import sqlite3

from config import DB_NAME


def is_new(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    connection.close()
    if (user_id,) not in users:
        return True
    return False


def get_users():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    connection.close()
    return [user[0] for user in users]


def get_users_with_access():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users WHERE access=1''').fetchall()
    connection.close()
    return [user[0] for user in users]


def get_user_role(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    user = cursor.execute('''SELECT role FROM users WHERE user_id = ?''', (user_id, )).fetchone()
    connection.close()
    return user[0]


def get_admins():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    admins = cursor.execute('''SELECT id FROM users WHERE role = 1''').fetchall()
    connection.close()
    return [admin[0] for admin in admins]


def get_new_script(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    script = cursor.execute('''SELECT id FROM scripts WHERE user_id = ? AND success IS NULL AND status NOT IN ("canceled", "created", "failed") ''', (user_id, )).fetchone()
    connection.close()
    return script[0] if script else None


def get_categories(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    categories = cursor.execute('''SELECT id, name FROM categories WHERE script_id = ?''', (script_id, )).fetchall()
    connection.close()
    d = {}
    for category in categories:
        d[category[1]] = category[0]
    return d if d else None


def get_raw_products(script_id, category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    products = cursor.execute('''SELECT id, raw_data FROM products WHERE script_id = ? AND category_id = ? AND article IS NULL ''', (script_id, category_id)).fetchall()
    connection.close()
    return [[product[0], product[1]] for product in products]


def get_template_category(category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    temp = cursor.execute('''SELECT template FROM categories WHERE id = ?''', (category_id,)).fetchone()
    connection.close()
    return temp[0]
