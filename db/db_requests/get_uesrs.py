import sqlite3

from config import DB_NAME


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
