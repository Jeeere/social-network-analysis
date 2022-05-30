"""
Analyzes collected threads
"""
import json
import matplotlib.pyplot as plt
import os

import database as db
from main import KEYWORDS
import timing

KEYWORDS = KEYWORDS
"""
KEYWORDS: dict = {
    "first_time_pregnancy": ["Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen", "Äitiys", "Ensiraskaus Oireet", "Ensiraskaus", "Ensiraskaus vinkkejä", "Ensiraskaus mitä odottaa", "Eka raskaus", "ensiraskaus kokemus"],
    "parents_and_family": ["Isä", "Äiti", "Vanhemmat", "Vanhemmuus", "YH Äiti", "YH Isä", "Sukulaiset", "Isovanhemmat", "Isoäiti", "Isoisä", "Setä", "Eno", "Täti", "Kummi", "Parisuhde"],
    "society": ["Yhteiskunta", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä"],
    "health_issues": ["Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola"],
    "social_services": ["Sosiaalipalvelut", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku"]
}
"""


def main():
    threads = db.get_threads(conn, 'SELECT * FROM THREADS WHERE ANALYZE=1')

    support = test_strength(threads)
    plot_strength(support)
    
    return


def test_strength(threads:list):
    """
    Tests strength of each category with a simple string matching of the keyword lists.\n
    Arguments:
        threads: list of threads to be tested.
    """
    print("Testing strength...")
    timing.log("Start testing strength")
    support = {
            "parents_and_family": 0,
            "society": 0,
            "health_issues": 0,
            "social_services": 0,
            "finance_and_wealth": 0
            }

    for thread in threads:
        thread = thread[5].replace("'", '"')
        thread_json = json.loads(thread)

        for reply_num, data in thread_json.items():
            # Test parents and family
            support["parents_and_family"] = support["parents_and_family"] + test_category_support("parents_and_family", data)
            # Test society
            support["society"] = support["society"] + test_category_support("society", data)
            # Test health issues
            support["health_issues"] = support["health_issues"] + test_category_support("health_issues", data)
            # Test social services
            support["social_services"] = support["social_services"] + test_category_support("social_services", data)
            # Test finance and wealth
            support["finance_and_wealth"] = support["finance_and_wealth"] + test_category_support("finance_and_wealth", data)
        
    return support


def plot_strength(support):
    """
    Traces a bar plot showing the proportion of each category in the collected database.
    """
    print("Plotting strengths...")
    values = list(support.values())
    width = 0.3

    fig, ax = plt.subplots(figsize=(9,6))
    ax.bar(list(support.keys()), values, width)
    for i, v in enumerate(values):
        ax.text(i - .15, v + 1000, str(v))
    plt.savefig("figures/strengths_transparent.png", dpi= "figure", format= "png", transparent= True)
    plt.savefig("figures/strengths.png", dpi= "figure", format= "png", transparent= False)

    return


def test_category_support(category:str, message:str):
    """
    
    """
    support = 0
    tested = []
    for keyword in KEYWORDS[category]:
        if keyword not in tested:
            support += message["text"].count(keyword)
            tested.append(keyword)
            # if message["text"].count(keyword) > 0:
            #     print(keyword + str(support))
    return support


if __name__ == "__main__":
    try:
        global conn
        conn = db.create_db_connection("threads.db")
        main()
        print("QUITTING...")
    except KeyboardInterrupt:
        print("QUITTING...")
    db.close_connection(conn)