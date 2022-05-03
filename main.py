from asyncore import loop
from cmath import e
import requests
from bs4 import *

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}

keywords = {
    "first_time_pregnancy": ["Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen", "Äitiys", "Oireet"],
    "parents_and_family": ["Isä", "Äiti", "Vanhemmat", "Vanhemmuus", "YH Äiti", "YH Isä", "Sukulaiset", "Isovanhemmat", "Isoäiti", "Isoisä", "Setä", "Eno", "Täti", "Kummi", "Parisuhde"],
    "society": ["Yhteiskunta", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä"],
    "health_issues": ["Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola"],
    "social_services": ["Sosiaalipalvelut", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku"]
}

threads = {}

def main():
    print("MAIN")
    search(keywords["first_time_pregnancy"])

    print(threads)
    print("Number of thrads collected: " + str(len(threads)))
    return

def search(keywords):
    """
    Calls search_by_keyword() with every keyword in list.
    """
    for keyword in keywords:
        search_by_keyword(keyword)
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
        print("Parsing page " + str(page))
        vauva_search = "https://www.vauva.fi/haku?page=" + str(page) + "&search_term=" + keyword_new
        request = requests.get(vauva_search, headers=headers)
        page += 1
        soup = BeautifulSoup(request.text, "html.parser")
        # Find threads
        threads = soup.find_all("div", attrs={"class":"teaser-column-content"})

        try:
            threads[0]
        except IndexError as e:
            print("Last page reached!")
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
    print("RESULTS TO DICT")
    for thread in data:
        if thread[0] not in threads.keys():
            threads.update({thread[0]: {"replies": thread[1]}})
    return


if __name__ == "__main__":
    main()