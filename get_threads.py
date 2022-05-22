"""
Searches vauva.fi for threads
"""
from bs4 import BeautifulSoup
from scrape_threads import try_request
import database as db
from sqlite3 import Connection

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
VAUVA = "https://www.vauva.fi"

def search(keywords: list, conn:Connection, last_page:int=-1):
    """
    Calls search_by_keyword() with every keyword in list.\n
    Arguments:
        keyword: list of keywords used for search
        last_page: last page to be searched as integer
    Returns:
        List of unique thread URLs
    """
    details = {}
    unique_urls = []
    for keyword in keywords:
        unique_urls_kw = 0
        urls, total = search_by_keyword(keyword, last_page)
        for url in urls:
            if url not in unique_urls:
                # Check if exists in database
                if db.check_new(url, conn):
                    unique_urls.append(url)
                    unique_urls_kw += 1
        keyword_details = {keyword:{"total_urls":total,"total_matching_urls":len(urls),"unique_matching_urls":unique_urls_kw}}
        details.update(keyword_details)

    return unique_urls, details


def search_by_keyword(keyword: str, last_page:int=-1):
    """
    Loops through all search results for given keyword and returns list of urls of threads of which replies exceed minimum amount.\n
    Arguments:
        keyword: keyword string used for search
        last_page: last page to be searched as integer
    Returns:
        List of found thread URLs
    """
    # TODO Threads missing from returned URLs (?)
    total = 0
    min_replies = 10
    keyword_new = keyword.lower().replace(" ", "%20").replace("ä", "a").replace("ö", "o").replace("å", "a")

    if keyword != keyword_new:
        print("SEARCHING BY: " + keyword + " -> " + keyword_new)
    else:
        print("SEARCHING BY: " + keyword)
    data = []

    page = 0
    while True:
        vauva_search = VAUVA + "/haku?page=" + str(page) + "&search_term=" + keyword_new
        request = try_request(url=vauva_search)
        soup = BeautifulSoup(request.text, "lxml")
        soup = soup.find("div", class_="region-main clearfix")
        # Find threads
        threads = soup.find_all("div", attrs={"class":"teaser-column-content"})

        try:
            threads[0]
        except IndexError as e:
            print("Last page reached! " + str(page-1))
            print("Total number of results with number of replies equal or more than " + str(min_replies) + ": " + str(len(data)))
            return data, total

        print("Parsing page " + str(page))
        
        # Loop over threads
        for thread in threads:
            total += 1
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
                data.append(VAUVA + url)

        if page == last_page:
            print("Given page reached!")
            print("Total number of results: " + str(len(data)))
            return data, total
        
        page += 1
