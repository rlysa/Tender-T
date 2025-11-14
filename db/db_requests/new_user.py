import sqlite3
import os.path
from config import DB_NAME


def add_new_user(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    users = cursor.execute('''SELECT id FROM users''').fetchall()
    if (user_id, ) not in users:
        cursor.execute('''INSERT INTO users (id) VALUES (?)''', (user_id, ))
        connection.commit()
    connection.close()
