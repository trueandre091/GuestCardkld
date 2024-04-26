import os
import sqlite3

DATABASE_DIR = "C:\\Users\\andre\\Desktop\\GuestCardkld\\DB"
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
                                        categories text NOT NULL
                                    ); """
    try:
        cursor.execute(table_creation_query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_user(user_id, username, start=True, likes="", categories=""):
    conn = create_connection()
    sql = ''' INSERT INTO users(id, username, start, likes, categories)
              VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (user_id, username, start, likes, categories))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
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


def update_user(user_id, username=None, start=None, likes=None, categories=None):
    conn = create_connection()
    sql = ''' UPDATE users
              SET username = ?,
                  start = ?,
                  likes = ?,
                  categories = ?
              WHERE id = ?'''
    try:
        cursor = conn.cursor()
        current_user = get_user_by_id(user_id)
        if not current_user:
            print("User not found.")
            return
        if categories is not None and categories not in current_user[4].split():
            categories = current_user[4] + " " + categories
        else:
            categories = current_user[4]

        if likes is not None and likes not in current_user[3].split():
            likes = current_user[3] + likes
        else:
            likes = current_user[3]

        data = (
            username if username is not None else current_user[1],
            start if start is not None else current_user[2],
            likes,
            categories,
            user_id
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


if __name__ == "__main__":
    create_table()
