import sqlite3
import hashlib

def create_users_table():

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        video_name TEXT,
        transcript TEXT,
        summary TEXT
    )
    """)

    conn.commit()

    conn.close()

create_users_table()

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(username, password):

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    hashed_password = hash_password(password)

    try:

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, hashed_password)
        )

        conn.commit()

        conn.close()

        return True

    except:

        conn.close()

        return False


def login_user(username, password):

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    hashed_password = hash_password(password)

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password)
    )

    data = c.fetchone()

    conn.close()

    return data


def save_history(username, video_name, transcript, summary):

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    c.execute(
        """
        INSERT INTO history
        (username, video_name, transcript, summary)
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            video_name,
            transcript,
            summary
        )
    )

    conn.commit()

    conn.close()


def get_history(username):

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    c.execute(
        """
        SELECT * FROM history
        WHERE username=?
        ORDER BY id DESC
        """,
        (username,)
    )

    data = c.fetchall()

    conn.close()

    return data


def get_single_history(history_id):

    conn = sqlite3.connect("users.db")

    c = conn.cursor()

    c.execute(
        """
        SELECT * FROM history
        WHERE id=?
        """,
        (history_id,)
    )

    data = c.fetchone()

    conn.close()

    return data
