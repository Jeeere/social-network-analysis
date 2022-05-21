"""
Searches vauva.fi for threads
"""
from bs4 import BeautifulSoup
import requests

HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
VAUVA = "https://www.vauva.fi"

def search(keywords: list, last_page:int=-1):
    """
    Calls search_by_keyword() with every keyword in list.\n
    Arguments:
        keyword: list of keywords used for search
        last_page: last page to be searched as integer
    Returns:
        List of unique thread URLs
    """
    unique_urls = []
    for keyword in keywords:
        urls = search_by_keyword(keyword, last_page)
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        
    return unique_urls


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
        vauva_search = VAUVA + "/haku?page=" + str(page) + "&search_term=" + keyword_new
        request = requests.get(vauva_search, headers=HEADERS)
        soup = BeautifulSoup(request.text, "lxml")
        soup = soup.find("div", class_="region-main clearfix")
        # Find threads
        threads = soup.find_all("div", attrs={"class":"teaser-column-content"})

        try:
            threads[0]
        except IndexError as e:
            print("Last page reached! " + str(page))
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
                data.append(VAUVA + url)

        if page == last_page:
            print("Given page reached!")
            print("Total number of results: " + str(len(data)))
            return data
        
        page += 1
