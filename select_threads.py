"""
Tool for selecting threads from database to be analyzed.
"""
from requests import JSONDecodeError
import database as db
import json

line = "=" * 50


def main():
    thread_num = 1
    threads = db.get_threads(conn, 'SELECT * FROM THREADS')
    thread_last = len(threads)

    f = open("backup.txt", "a")
    f.close()

    for thread in threads:
        
        with open("backup.txt", "r+") as f:
            backup = f.read()
            print(backup)
            if backup == "":
                f.write("0")
            elif int(backup) >= thread_num:
                print("skipping")
                thread_num += 1
                continue

            # print(thread)
            url = thread[0]
            thread = thread[5].replace("'", '"')
            # print(thread)
            try:
                thread_json = json.loads(thread)
            except json.decoder.JSONDecodeError as e:
                print(thread)
                print(e)
                thread_num += 1
                continue
            messages = list(thread_json.values())
            op = messages[0]
            title = op["title"]
            post = op["text"]

            print(line)
            print("TITLE   " + str(thread_num) + "/" + str(thread_last))
            print(url)
            print(title)
            print(line)
            print("POST")
            print(post)
            print(line)

            answer = shit(url, title, post)

            if answer == 1:
                sql = '''
                    UPDATE THREADS
                    SET ANALYZE = 1
                    WHERE URL = ?
                    '''
                cursor = conn.cursor()
                cursor.execute(sql,(url,))
                conn.commit()
                cursor.close()
            elif answer == 0:
                sql = '''
                    UPDATE THREADS
                    SET ANALYZE = 0
                    WHERE URL = ?
                    '''
                cursor = conn.cursor()
                cursor.execute(sql,(url,))
                conn.commit()
                cursor.close()
            
            f.seek(0)
            f.write(str(thread_num))
        thread_num += 1
    return


def shit(url, title, post):
    """
    Asks if the presented thread should be analyzed.
    """
    answer = input("Analyze? (y/n): ").lower().strip()

    if answer == "y":
        analyze = 1
    elif answer == "n":
        analyze = 0
    else:
        print("Faulty input!!!")
        shit(url, title, post)
    return analyze


if __name__ == "__main__":
    try:
        global conn
        conn = db.create_db_connection("threads.db")
        main()
    except KeyboardInterrupt:
        print("\nQUITTING...")
    db.close_connection(conn)
