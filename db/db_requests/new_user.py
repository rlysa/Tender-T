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


def add_new_user(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    if (user_id, ) not in users:
        cursor.execute('''INSERT INTO users (id, role) VALUES (?, ?)''', (user_id, 2))
        connection.commit()
    connection.close()
