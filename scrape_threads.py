"""
Scrapes wanted vauva.fi threads
"""
from datetime import datetime
from sqlite3 import Connection
import time
from bs4 import BeautifulSoup
import requests

import database as db


HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
TOTAL_REQUESTS = 0


def get_threads(threads: list, conn: Connection):
    """
    Calls get_thread() with given thread addresses.\n
    Arguments:
        threads: list of unique URLs
        conn: SQLite database connection
    """
    for thread in threads:
        thread = get_thread(thread)
        # print(metadata)
        # print(thread)
        # print(len(thread))
        db.insert_thread(conn, thread)

    return


def get_thread(url: str):
    """
    Gets thread from given address.\n
    Arguments:
        url: URL to thread as string
    Returns:
        Dictionary containing everything about a thread
    """
    total_likes = 0
    total_dislikes = 0

    print("Getting thread from " + url)
    request = try_request(url=url)
    soup = BeautifulSoup(request.text, "lxml")
    soup = soup.find("div", attrs={"class":"region-main"})

    # Original post (OP) Username
    try:
        username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full anonymous"}).get_text()
    except AttributeError as e:
        try:
            username = soup.find("a", href=True, attrs={"title":"Näytä käyttäjäprofiili.", "class":"username"})["href"]
        except TypeError as a:
            try:
                username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full"}).get_text()
            except AttributeError:
                username = ""

    # OP Timestamp
    time_date_string = soup.find("div", attrs={"class":"field field-name-post-date field-type-ds field-label-hidden view-mode-full"}).get_text().replace("klo ", "").replace("| ", "").strip()
    time_date = datetime.strptime(time_date_string, r"%H:%M %d.%m.%Y")
    timestamp = datetime.timestamp(time_date)
    category = soup.find("a", href=True, attrs={"class":"section-link"}).get_text()

    # OP Rating
    try:
        rating = soup.find_all("div", class_="form-item form-type-item")[1]
        likes, dislikes = get_rating(rating)
    except IndexError:
        likes, dislikes = 0, 0
    total_likes += likes
    total_dislikes += dislikes

    # OP Post
    title = soup.find("div", attrs={"class":"field-item even", "property":"dc:title"}).get_text(strip=True)
    # Remove quotes for later JSON decoding
    title = title.replace("'", "").replace('"', '').replace(u"\xa0", " ")
    try:
        body = soup.find("div", attrs={"class":"field field-name-body field-type-text-with-summary field-label-hidden view-mode-full"}).get_text(strip=True).strip()
        # Remove quotes for later JSON decoding
        body = body.replace("'", "").replace('"', '').replace(u"\xa0", " ")
    except AttributeError:
        body = ""

    # Comments section
    comment_section = soup.find("section", class_="comments comment-wrapper")
    num_replies = int(comment_section.find("h3", attrs={"class":"comments__title title"}).get_text().replace("Kommentit (", "").replace(")",""))

    # Initialize dict to be returned
    thread = {"url":url, "category":category, "replies":num_replies, "total_likes":0, "total_dislikes":0, "thread":{}}
    thread["thread"].update({"0": {"user":str(username), "timestamp":timestamp, "likes":likes, "dislikes":dislikes, "title":title, "text":body}})

    # Handle comments section
    page = 0
    getting_comments = True
    while getting_comments:
        comments = comment_section.find_all("div", attrs={"class":"sanoma-comment"})
        
        for comment in comments:
            try:
                comment.find("blockquote").extract()
            except AttributeError as e:
                # No quote
                pass
            # TODO Fix user links (only gets username)
            try:
                com_user = comment.find("span", attrs={"class":"username-wrapper"}).find("a").get_href()
            except:
                try:
                    com_user = comment.find("span", attrs={"class":"username-wrapper"}).get_text()
                except AttributeError:
                    com_user = ""
        
            com_number = int(comment.find("div", class_="comment-number").get_text().split("/")[0])

            # Rating
            try:
                rating = comment.find("div", class_="bottom clearfix").find("div", class_="right")
                com_likes, com_dislikes = get_rating(rating)
            except AttributeError as e:
                print(e)
                print(comment)
                com_likes, com_dislikes = 0,0
                pass

            # Timestamp
            com_time_date_string = comment.find("div", attrs={"class":"field field-name-post-date field-type-ds field-label-hidden view-mode-full"}).get_text().replace("klo ", "").replace("| ", "").strip()
            com_time_date = datetime.strptime(com_time_date_string, r"%H:%M %d.%m.%Y")
            com_timestamp = datetime.timestamp(com_time_date)

            com_text = comment.find("div", class_="field field-name-comment-body field-type-text-long field-label-hidden view-mode-full").get_text(strip=True).strip()
            com_text = com_text.replace("'", "").replace('"', '').replace(u"\xa0", " ")

            # Add reply to thread
            com_likes, com_dislikes = int(com_likes), int(com_dislikes)
            reply = {str(com_number): {"user":com_user, "timestamp":com_timestamp, "likes":com_likes, "dislikes":com_dislikes, "text":com_text}}
            thread["thread"].update(reply)
            total_likes += com_likes
            total_dislikes += com_dislikes

            # Check if last reply
            if com_number >= num_replies:
                getting_comments = False

        # Get next page
        page += 1
        request = try_request(url=url + "?page=" + str(page))
        soup = BeautifulSoup(request.text, "lxml")
        comment_section = soup.find("section", class_="comments comment-wrapper")
    
    thread["total_likes"], thread["total_dislikes"] = total_likes, total_dislikes
    return thread


def get_rating(soup: BeautifulSoup):
    """
    Gets likes and dislikes from given soup.\n
    Arguments:
        soup: small html section as BeautifulSoup
    Returns:
        (likes, dislikes) as integer
    """
    likes = soup.find("li", attrs={"class":"first"}).get_text().replace("ylös\n", "")
    if "k" in likes:
        likes = int(float(likes.replace("k","")) * 1000)
    else:
        int(likes)
    dislikes = soup.find("li", attrs={"class":"last"}).get_text().replace("alas\n", "")
    if "k" in dislikes:
        dislikes = int(float(dislikes.replace("k","")) * 1000)
    else:
        int(dislikes)

    return int(likes), int(dislikes)


def try_request(url:str, headers:dict=HEADERS, s:int=15):
    """
    Attempts to perform a get request. On failure waits x seconds and tries again.\n
    Arguments:
        url: URL to be requested
        headers: Headers for request
        s: Seconds before retry
    Returns:
        Get request response
    """
    while True:
        try:
            request = requests.get(url, headers=headers)
            global TOTAL_REQUESTS
            TOTAL_REQUESTS += 1
            return request
        except:
            print("Trying again in " + str(s) + " seconds...")
            time.sleep(s)
