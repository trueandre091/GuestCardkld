import os
import sqlite3

DATABASE_DIR = "C:\\Users\\andre\\Desktop\\Проекты\\ЧатБот\\pythonProject3\\.venv\\DB"
DATABASE_NAME = "DataBase.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

def create_connection():
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    table_creation_query = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        username text NOT NULL,
                                        start text NOT NULL,
                                        card boolean NOT NULL,
                                        info text NOT NULL
                                    ); """
    try:
        cursor.execute(table_creation_query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_user(user_id, username, start, card=False, info=""):
    conn = create_connection()
    sql = ''' INSERT INTO users(id, username, start, card, info)
              VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, username, start, card, info))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_user(user_id):
    conn = create_connection()
    sql = 'SELECT * FROM users WHERE id=?'
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        return user
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
