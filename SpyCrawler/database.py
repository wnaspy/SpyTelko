import sqlite3
from config import DATABASE_FILE


def get_connection():
    return sqlite3.connect(DATABASE_FILE)


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message_id INTEGER,
        text TEXT,
        urls TEXT,
        UNIQUE(channel, message_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message_id INTEGER,
        file_name TEXT,
        file_path TEXT,
        UNIQUE(channel, message_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_state (
        channel TEXT PRIMARY KEY,
        last_message_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


def get_last_message_id(channel):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_message_id FROM crawl_state WHERE channel=?",
        (channel,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]

    return 0


def update_last_message_id(channel, message_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO crawl_state(channel,last_message_id)
    VALUES (?,?)
    ON CONFLICT(channel)
    DO UPDATE SET last_message_id=excluded.last_message_id
    """, (channel, message_id))

    conn.commit()
    conn.close()


def insert_news(channel, message_id, text, urls):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO news(channel,message_id,text,urls)
    VALUES (?,?,?,?)
    """, (channel, message_id, text, urls))

    conn.commit()
    conn.close()


def insert_document(channel, message_id, file_name, file_path):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO documents(channel,message_id,file_name,file_path)
    VALUES (?,?,?,?)
    """, (channel, message_id, file_name, file_path))

    conn.commit()
    conn.close()