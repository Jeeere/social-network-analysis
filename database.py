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


def create_db(db_path: str, reinit:bool=True):
    """
    Create a connection to an SQLite database and reinitialize it.\n
    Arguments:
        db_path: string describing path to wanted .db file
        reinit: boolean describing if table should be reinitialized
    Returns:
        Database connection
    """
    try:
        conn: Connection = sqlite3.connect(db_path)
    except:
        print("ERROR: Error creating db connection!")
    else:
        cursor = conn.cursor()

        # SQL for creating table
        if reinit:
            # Delete existing table
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
        else:
            sql ='''
                CREATE TABLE IF NOT EXISTS THREADS(
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
    try:
        cursor.execute(sql, (thread["url"], thread["category"], thread["replies"], thread["total_likes"], thread["total_dislikes"], str(thread["thread"]), False))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Thread already exists in database!")
    cursor.close()

    print("Thread inserted to database")
    return cursor.lastrowid


def check_new(url:str, conn:Connection):
    """
    Check if given thread is new to the database.\n
    Arguments:
        url: URL to thread as string
        conn: database connection
    Returns:
        True if thread not in database, 
        False otherwise
    """
    cursor = conn.cursor()
    sql='SELECT EXISTS (SELECT 1 FROM THREADS WHERE URL=?) LIMIT 1'
    # Query returns 1 if url exists and 0 if not.
    check=cursor.execute(sql,(url,)) 
    if check.fetchone()[0]==0:
        cursor.close()
        return True
    else:
        cursor.close()
        return False
