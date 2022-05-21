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
        conn: Connection = sqlite3.connect(db_path)
        return conn
    except:
        print("ERROR: Error creating db connection!")  


def create_db(db_path: str):
    """
    Create a connection to an SQLite database and reinitialize it.\n
    Arguments:
        db_path: string describing path to wanted .db file
    Returns:
        Database connection
    """
    try:
        conn: Connection = sqlite3.connect(db_path)
    except:
        print("ERROR: Error creating db connection!")
    else:
        cursor = conn.cursor()

        # Delete existing table
        cursor.execute('DROP TABLE THREADS')

        # SQL for creating new table
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

        cursor.execute(sql)
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


def insert_thread(conn: Connection, thread: dict):
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
    cursor.execute(sql, (thread["url"], thread["category"], thread["replies"], thread["total_likes"], thread["total_dislikes"], str(thread["thread"]), False))
    conn.commit()
    cursor.close()

    print("Thread inserted to database")
    return cursor.lastrowid
