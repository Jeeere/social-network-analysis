from datetime import datetime
import requests
from bs4 import *
import lxml
import json
import database as db

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}

keywords = {
    "first_time_pregnancy": ["Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen", "Äitiys", "Ensiraskaus Oireet", "Ensiraskaus", "Ensiraskaus vinkkejä", "Ensiraskaus mitä odottaa", "Eka raskaus", "ensiraskaus kokemus"],
    "parents_and_family": ["Isä", "Äiti", "Vanhemmat", "Vanhemmuus", "YH Äiti", "YH Isä", "Sukulaiset", "Isovanhemmat", "Isoäiti", "Isoisä", "Setä", "Eno", "Täti", "Kummi", "Parisuhde"],
    "society": ["Yhteiskunta", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä"],
    "health_issues": ["Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola"],
    "social_services": ["Sosiaalipalvelut", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku"]
}
duplicates = 0
# ID, URL, Timestamp, post, likes, dislikes, replies, category, user
#(url, username, title, body, category, timestamp, likes, dislikes, num_replies)
threads = {}

# ID, {comment, timestamp, likes, dislikes, user}
replies = {}

unique_urls = []

vauva = "https://www.vauva.fi"


def main():
    print("MAIN")
    conn = db.create_db("threads.db")

    thread_urls = search(keywords["first_time_pregnancy"])
    set_unique_urls(thread_urls)
    #print(threads)
    print("Number of thrads collected: " + str(len(unique_urls)))
    thread = get_threads(unique_urls, conn)
    # results_to_dict(thread)
    db.close_connection(conn)

    return


def search(keywords):
    """
    Calls search_by_keyword() with every keyword in list.
    """
    data = []
    for keyword in keywords:
        data.extend(search_by_keyword(keyword))
        break
        
    return data


def search_by_keyword(keyword):
    """
    Loops through all search results for given keyword and returns (url, number of replies) if number of replies exceeds minimum requirement.
    """
    min_replies = 10
    keyword_new = keyword.lower().replace(" ", "%20").replace("ä", "a").replace("ö", "o").replace("å", "a")
    if keyword != keyword_new:
        print("SEARCHING BY: " + keyword + " -> " + keyword_new)
    else:
        print("SEARCHING BY: " + keyword)
    data = []

    page = 0
    while True:
        print("Parsing page " + str(page))
        vauva_search = vauva + "/haku?page=" + str(page) + "&search_term=" + keyword_new
        request = requests.get(vauva_search, headers=headers)
        soup = BeautifulSoup(request.text, "lxml")
        soup = soup.find("div", class_="region-main clearfix")
        # Find threads
        threads = soup.find_all("div", attrs={"class":"teaser-column-content"})

        try:
            threads[0]
        except IndexError as e:
            print("Last page reached! " + str(page))
            #print(data)
            print("Total number of results: " + str(len(data)))
            return data
        
        # Loop over threads
        for thread in threads:
            # Get number of replies
            try:
                replies = int(thread.find("span", attrs={"class":"count"}).get_text())
            except AttributeError as e:
                print("Error on page " + str(page) + ": " + str(e) + ", skipping.")
                page += 1
                continue
            # If less than minimum amount of replies, ignore thread
            if replies >= min_replies:
                # Find all anchor elements with href
                hrefs = thread.find_all('a', href=True)
                # Get url to thread
                url = hrefs[3]["href"]
                print(url)
                # Create duple of url and number of replies
                data.append(vauva + url)
        
        page += 1


def results_to_dict(data):
    """
    Adds new threads to dictionary
    """
    for thread in data:
        if list(thread.keys())[0] not in threads.keys():
            threads.update(thread)

    print(threads)
    return


def set_unique_urls(urls):
    meme = ""
    for url in urls:
        if url not in unique_urls:
            unique_urls.append(url)
            meme += url + ",0\n"
    
    with open("threads.csv", "w+") as f:
        f.write(meme)

    return


def get_threads(threads, conn):
    """
    Calls get_thread() with given thread addresses
    """
    data = []
    for thread in threads:
        thread, metadata = get_thread(thread)
        # data.append(post_details)
        print(metadata)
        print(thread)
        print(len(thread))

        db.insert_thread(conn, metadata, thread)

    return data


def get_thread(url):
    """
    Gets thread from given address.
    """
    thread = {"url":url, "thread":{}}
    total_likes = 0
    total_dislikes = 0
    print("Getting thread from " + url)
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "lxml")
    soup = soup.find("div", attrs={"class":"region-main"})

    # Username
    try:
        username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full anonymous"}).get_text()
    except AttributeError as e:
        try:
            username = soup.find("a", href=True, attrs={"title":"Näytä käyttäjäprofiili.", "class":"username"})["href"]
        except TypeError as a:
            username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full"}).get_text()

    # Timestamp
    time_date_string = soup.find("div", attrs={"class":"field field-name-post-date field-type-ds field-label-hidden view-mode-full"}).get_text().replace("klo ", "").replace("| ", "").strip()
    time_date = datetime.strptime(time_date_string, r"%H:%M %d.%m.%Y")
    timestamp = datetime.timestamp(time_date)
    category = soup.find("a", href=True, attrs={"class":"section-link"}).get_text()

    # Rating
    rating = soup.find_all("div", class_="form-item form-type-item")[1]
    likes, dislikes = get_rating(rating)

    # Post
    title = soup.find("div", attrs={"class":"field-item even", "property":"dc:title"}).get_text()
    body = soup.find("div", attrs={"class":"field field-name-body field-type-text-with-summary field-label-hidden view-mode-full"}).get_text().strip()

    # Comments
    comment_section = soup.find("section", class_="comments comment-wrapper")
    num_replies = int(comment_section.find("h3", attrs={"class":"comments__title title"}).get_text().replace("Kommentit (", "").replace(")",""))

    likes, dislikes = int(likes), int(dislikes)
    op = {0: {"user":username, "timestamp":timestamp, "likes":likes, "dislikes":dislikes, "title":title, "text":body}}
    thread["thread"].update(op)
    total_likes += likes
    total_dislikes += dislikes

    page = 0
    getting_comments = True
    while getting_comments:
        #print(url + "?page=" + str(page))
        comments = comment_section.find_all("div", attrs={"class":"sanoma-comment"})
        #print(comments[0])
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

            com_text = comment.find("div", class_="field field-name-comment-body field-type-text-long field-label-hidden view-mode-full").get_text().strip()

            # Add reply to thread
            com_likes, com_dislikes = int(com_likes), int(com_dislikes)
            reply = {com_number: {"user":com_user, "timestamp":com_timestamp, "likes":com_likes, "dislikes":com_dislikes, "text":com_text}}
            thread["thread"].update(reply)
            total_likes += com_likes
            total_dislikes += com_dislikes

            # Check if last reply
            if com_number >= num_replies:
                getting_comments = False

        # Get next page
        page += 1
        request = requests.get(url + "?page=" + str(page))
        soup = BeautifulSoup(request.text, "lxml")
        comment_section = soup.find("section", class_="comments comment-wrapper")

    #details = {url: {"user":username, "timestamp":timestamp, "category":category, "likes":likes, "dislikes":dislikes, "replies":num_replies, "title":title, "text":body}}
    metadata = {"url":url, "category":category, "replies":num_replies, "total_likes":total_likes, "total_dislikes":total_dislikes}
    
    return thread, metadata


def get_rating(soup):
    """
    Gets likes and dislikes from given soup
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

    return likes, dislikes


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("QUITTING...")
