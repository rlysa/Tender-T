import sqlite3
import os

from config import DB_NAME
from src.__all_func import save_result


def add_new_script(name, user_id, product_categories, key_words, products):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    new_script = cursor.execute('''INSERT INTO scripts (name, user_id) VALUES (?, ?) RETURNING id''', (name, user_id)).fetchone()[0]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, f'files/{new_script}')

    os.makedirs(path, exist_ok=True)
    path = f'{path}'.replace('\\', '/')
    save_result(f'{path}/categories.txt', product_categories)
    save_result(f'{path}/keywords.txt', key_words)
    save_result(f'{path}/products.txt', products)
    save_result(f'{path}/history.txt', '')
    file_1 = cursor.execute('''INSERT INTO files (path, name, script_id) VALUES (?, ?, ?)''', (path, 'categories.txt', new_script))
    file_2 = cursor.execute('''INSERT INTO files (path, name, script_id) VALUES (?, ?, ?)''', (path, 'keywords.txt', new_script))
    file_3 = cursor.execute('''INSERT INTO files (path, name, script_id) VALUES (?, ?, ?)''', (path, 'products.txt', new_script))
    file_4 = cursor.execute('''INSERT INTO files (path, name, script_id) VALUES (?, ?, ?)''', (path, 'history.txt', new_script))
    connection.commit()
    connection.close()


if __name__ == '__main__':
    print(os.path.abspath('files'))
