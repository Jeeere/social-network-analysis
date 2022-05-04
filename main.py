from datetime import datetime
import requests
from bs4 import *

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
threads = {}

# ID, {comment, timestamp, likes, dislikes, user}
replies = {}

vauva = "https://www.vauva.fi"

def main():
    print("MAIN")
    search(keywords["first_time_pregnancy"])

    #print(threads)
    print("Number of thrads collected: " + str(len(threads)))
    get_threads(threads)
    return

def search(keywords):
    """
    Calls search_by_keyword() with every keyword in list.
    """
    for keyword in keywords:
        search_by_keyword(keyword)
        break
    return

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
        #print("Parsing page " + str(page))
        vauva_search = vauva + "/haku?page=" + str(page) + "&search_term=" + keyword_new
        request = requests.get(vauva_search, headers=headers)
        page += 1
        soup = BeautifulSoup(request.text, "html.parser")
        # Find threads
        threads = soup.find_all("div", attrs={"class":"teaser-column-content"})

        try:
            threads[0]
        except IndexError as e:
            #print("Last page reached!")
            #print(data)
            print("Total number of results: " + str(len(data)))
            results_to_dict(data)
            return data
        
        # Loop over threads
        for thread in threads:
            # Get number of replies
            try:
                replies = int(thread.find("span", attrs={"class":"count"}).get_text())
            except AttributeError as e:
                print("Error on page " + str(page) + ": " + str(e) + ", skipping.")
                continue
            # If less than minimum amount of replies, ignore thread
            if replies >= min_replies:
                # Find all anchor elements with href
                hrefs = thread.find_all('a', href=True)
                # Get url to thread
                url = hrefs[3]["href"]
                # Create duple of url and number of replies
                data.append((url, replies))

def results_to_dict(data):
    """
    Adds new threads to dictionary
    """
    #print("RESULTS TO DICT")
    for thread in data:
        if thread[0] not in threads.keys():
            threads.update({thread[0]: {"replies": thread[1]}})
        else:
            pass
    return

def get_threads(threads):
    """
    Calls get_thread() with given thread addresses
    """
    for thread in list(threads.keys()):
        print(get_thread(thread))
    return

def get_thread(addr):
    """
    Gets thread from given address.
    """
    url = vauva + addr
    print("Getting thread from " + url)
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    soup = soup.find("div", attrs={"class":"region-main"})
    #print(soup)

    title = soup.find("div", attrs={"class":"field-item even", "property":"dc:title"}).get_text()
    try:
        username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full anonymous"}).get_text()
    except AttributeError as e:
        try:
            username = soup.find("a", href=True, attrs={"title":"Näytä käyttäjäprofiili.", "class":"username"})["href"]
        except TypeError as a:
            username = soup.find("div", attrs={"class":"user-name extra-field-author view-mode-full view-mode-full"}).get_text()
    time_date_string = soup.find("div", attrs={"class":"field field-name-post-date field-type-ds field-label-hidden view-mode-full"}).get_text().replace("klo ", "").replace("| ", "").strip()
    time_date = datetime.strptime(time_date_string, r"%H:%M %d.%m.%Y")
    timestamp = datetime.timestamp(time_date)
    category = soup.find("a", href=True, attrs={"class":"section-link"}).get_text()
    rating = soup.find_all("div", class_="form-item form-type-item")[1]
    likes = int(rating.find("li", attrs={"class":"first"}).get_text().replace("ylös\n", ""))
    dislikes = int(rating.find("li", attrs={"class":"last"}).get_text().replace("alas\n", ""))
    
    return username, title, category, timestamp, likes, dislikes

if __name__ == "__main__":
    main()
