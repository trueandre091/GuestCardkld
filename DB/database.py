import os
import sqlite3
from datetime import datetime, timedelta


DATABASE_DIR = os.path.dirname(__file__)
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
                                        likes text NOT NULL,
                                        entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                        last_timestamp DATETIME NOT NULL
                                    ); """
    try:
        cursor.execute(table_creation_query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_statistics_table():
    conn = create_connection()
    cursor = conn.cursor()
    table_creation_query = """ CREATE TABLE IF NOT EXISTS statistics (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        user_id integer NOT NULL,
                                        event text NOT NULL,
                                        info text NOT NULL,
                                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """
    try:
        cursor.execute(table_creation_query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_user(user_id, username, start=True, likes="",
             last_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    conn = create_connection()
    sql = ''' INSERT INTO users(id, username, start, likes, last_timestamp)
              VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, username, start, likes, last_timestamp))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_event(user_id, event, info=""):
    """Add an event for a user to the statistics table."""
    conn = create_connection()
    sql = ''' INSERT INTO statistics(user_id, event, info)
              VALUES(?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, event, info))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def get_all_users():
    """Retrieve all users and their data from the database."""
    conn = create_connection()
    sql = 'SELECT * FROM users'
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        all_users = cursor.fetchall()
        return all_users
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def reset_likes(user_id):
    conn = create_connection()
    sql = ''' UPDATE users
                  SET likes = ?
                  WHERE id = ?'''
    try:
        cursor = conn.cursor()
        current_user = get_user_by_id(user_id)
        if not current_user:
            print("User not found.")
            return

        likes = ""
        data = (
            likes,
            user_id,
        )

        cursor.execute(sql, data)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def update_user(user_id, username=None, start=None, likes=None, entry_timestamp=None,
                last_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    conn = create_connection()
    sql = ''' UPDATE users
              SET username = ?,
                  start = ?,
                  likes = ?,
                  entry_timestamp = ?,
                  last_timestamp = ?
              WHERE id = ?'''
    try:
        cursor = conn.cursor()
        current_user = get_user_by_id(user_id)
        if not current_user:
            print("User not found.")
            return

        if likes is not None and likes not in current_user[3].split(";"):
            likes = current_user[3] + likes + ";"
        elif likes is not None and likes in current_user[3].split(";"):
            # start = current_user[3].find(likes + ";")
            likes = current_user[3].replace(likes + ";", "")
        else:
            likes = current_user[3]

        data = (
            username if username is not None else current_user[1],
            start if start is not None else current_user[2],
            likes,
            current_user[5],
            last_timestamp,
            user_id,
        )

        cursor.execute(sql, data)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_user_by_id(user_id):
    """Retrieve a user by their ID from the database."""
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


# Функция для получения статистики за определенный период
def get_statistics(start_date, end_date):
    conn = create_connection()
    sql = '''SELECT event, info, timestamp FROM statistics WHERE timestamp BETWEEN ? AND ?'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (start_date, end_date))
        statistics = cursor.fetchall()
        return statistics
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_active_users(start_date, end_date):
    conn = create_connection()
    active_users = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, last_timestamp FROM users WHERE last_timestamp BETWEEN ? AND ?",
                    (start_date, end_date))
        active_users = cur.fetchall()
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()
    if conn:
        conn.close()
    return active_users


if __name__ == "__main__":
    create_table()
    create_statistics_table()
