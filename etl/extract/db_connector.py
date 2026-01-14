import sqlite3

from config import DB_NAME


def get_scripts():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    scripts = cursor.execute('''SELECT id, name FROM scripts''', ).fetchall()
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
    keywords = cursor.execute(f'''SELECT name FROM keywords WHERE script_id = ?''', (script_id,)).fetchall()
    connection.close()
    return [keyword[0] for keyword in keywords]


def get_not_looked_cards(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cards = cursor.execute(f'''SELECT id, number, link FROM cards WHERE script_id = ? AND status = "new" ''', (script_id,)).fetchall()
    connection.close()
    return [[i for i in card] for card in cards]


def get_not_filtered_lots(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots = cursor.execute(f'''SELECT l.id, l.name FROM lots l JOIN cards c ON l.card_id = c.id WHERE c.script_id = ? AND l.status = "new" ''',(script_id,)).fetchall()
    connection.close()
    return [[i for i in lot] for lot in lots]


def get_all_cards(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cards = cursor.execute(f'''SELECT id FROM cards WHERE script_id = ? AND status = "get_lots" ''', (script_id,)).fetchall()
    connection.close()
    return [card[0] for card in cards]


def get_filtered_lots_for_card(card_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots = cursor.execute(f'''SELECT id FROM lots WHERE card_id = ? AND status = "filtered" ''',(card_id,)).fetchall()
    connection.close()
    return [lot[0] for lot in lots]


def get_categories(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    categories = cursor.execute(f'''SELECT id, name FROM categories WHERE script_id = ?''', (script_id,)).fetchall()
    connection.close()
    return [[i for i in category] for category in categories]


def get_filtered_lots(script_id, category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots = cursor.execute(f'''SELECT l.id, l.name, l.description FROM lots l JOIN cards c ON l.card_id = c.id WHERE c.script_id = ? AND l.status = "filtered" AND l.category_id = ? ''',(script_id, category_id)).fetchall()
    connection.close()
    return [f'{lot[0]}: {lot[1]} ({lot[2]}' for lot in lots]


def get_products(script_id, category_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    products = cursor.execute(f'''SELECT id, name, cost FROM products WHERE script_id = ? AND category_id = ? ''',(script_id, category_id)).fetchall()
    connection.close()
    return [f'{product[0]}: {product[1]}: {product[2]}' for product in products]


def get_filtered_cards(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cards = cursor.execute(f'''SELECT id FROM cards WHERE script_id = ? AND status = "processed" ''', (script_id,)).fetchall()
    connection.close()
    return [card[0] for card in cards]


def get_matched_lots_for_card(card_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots = cursor.execute(f'''SELECT id FROM lots WHERE card_id = ? AND status = "matched" ''',(card_id,)).fetchall()
    connection.close()
    return [lot[0] for lot in lots]


def get_relevant_cards(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cards = cursor.execute(f'''SELECT id, number, name, cost, region, link FROM cards WHERE script_id = ? AND status = "processed" ''', (script_id,)).fetchall()
    connection.close()
    return [[i for i in card] for card in cards]


def get_matched_lots_products_for_card(card_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots_products = cursor.execute(f'''SELECT l.id, l.article, l.name, l.description, l.count, l.cost, p.article, p.name, p.cost FROM lots l JOIN products p ON l.match_product_id = p.id WHERE card_id = ? AND status = "matched" ''',(card_id,)).fetchall()
    connection.close()
    return [[i for i in lp] for lp in lots_products]


def get_not_matched_lots(card_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots = cursor.execute(f'''SELECT name FROM lots WHERE card_id = ? AND status = "finished" ''', (card_id,)).fetchall()
    connection.close()
    return [lot[0] for lot in lots]


def get_matched_lots_count(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    lots_count = cursor.execute(f'''SELECT COUNT(l.id) FROM lots l JOIN cards c ON l.card_id = c.id WHERE c.script_id = ? AND l.status = "matched"''',(script_id, )).fetchone()
    connection.close()
    return lots_count[0]


def get_last_collect_date(script_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    last_collect_date = cursor.execute(f'''SELECT last_collect_date FROM scripts WHERE id = ? ''', (script_id,)).fetchone()
    connection.close()
    return last_collect_date
