import sqlite3
from config import DB_NAME


def change_access(user_id):
    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute('''UPDATE users SET access=1 WHERE id="{}"'''.format(user_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        raise Exception(f'Не удалось изменить доступ {e}')
