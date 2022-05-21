"""
Handles database interactions
"""
from multiprocessing.connection import Connection
import sqlite3

def create_db_connection(db_path: str):
    """
    Create a connection to an SQLite database.\n
    Arguments:
        db_path: string describing path to wanted .db file
    Returns:
        Database connection
    """
    try:
        conn = None
        conn: Connection = sqlite3.connect(db_path)
    except:
        print("ERROR: Error creating db connection!")
    else:
        return conn


def create_db(db_path: str):
    """
    Create a connection to an SQLite database and reinitialize it.\n
    Arguments:
        db_path: string describing path to wanted .db file
    Returns:
        Database connection
    """
    conn = None
    try:
        conn: Connection = sqlite3.connect(db_path)
    except:
        print("ERROR: Error creating db connection!")
    else:
        cursor = conn.cursor()

        cursor.execute('DROP TABLE THREADS')

        sql ='''
            CREATE TABLE THREADS(
            URL TEXT PRIMARY KEY,
            CATEGORY TEXT,
            REPLIES INTEGER,
            TOTAL_LIKES INTEGER,
            TOTAL_DISLIKES INTEGER,
            THREAD TEXT,
            ANALYZE BOOLEAN)
            '''

        sql_thread = '''
            CREATE TABLE IF THREAD(
            URL TEXT PRIMARY KEY,
            THREAD TEXT)
            '''

        cursor.execute(sql)
        # cursor.execute(sql_thread)
        conn.commit()
        cursor.close()

        return conn


def close_connection(conn: Connection):
    """
    Closes database connection.\n
    Arguments:
        conn: sqlite3 Connection to be closed
    """
    conn.close()
    return


def insert_thread(conn: Connection, data: dict, thread: dict):
    """
    Inserts thread metadata into db.\n
    Arguments:
        conn: sqlite3 Connection
        data: dictionary containing metadata
    Returns:
        cursror.lastrowid
    """
    sql = '''
        INSERT INTO THREADS(
        URL, CATEGORY, REPLIES, TOTAL_LIKES, TOTAL_DISLIKES, THREAD, ANALYZE
        ) VALUES (
        ?, ?, ?, ?, ?, ?, ?
        )'''

    cursor = conn.cursor()
    cursor.execute(sql, (data["url"], data["category"], data["replies"], data["total_likes"], data["total_dislikes"], str(thread["thread"]), False))
    conn.commit()
    cursor.close()

    print("Metadata inserted to database")
    return cursor.lastrowid
