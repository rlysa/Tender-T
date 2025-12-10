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
