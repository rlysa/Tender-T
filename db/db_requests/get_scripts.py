import sqlite3

from config import DB_NAME


def get_scripts(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    scripts = cursor.execute(F'''SELECT * FROM scripts WHERE user_id="{user_id}"''').fetchall()
    scripts_d = {}
    for script in scripts:
        scripts_d[script[0]] = script[1]
    files = cursor.execute(f'''SELECT * FROM files WHERE script_id in ({', '.join([f'"{script[0]}"' for script in scripts])})''').fetchall()
    return [[script[1]] + [file[2] + '/' + file[1] for file in files if file[3] == script[0]] for script in scripts]
