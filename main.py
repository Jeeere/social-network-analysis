import database as db
import get_threads as gt
import scrape_threads as st
import timing

KEYWORDS: dict = {
    "first_time_pregnancy": ["Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen", "Äitiys", "Ensiraskaus Oireet", "Ensiraskaus", "Ensiraskaus vinkkejä", "Ensiraskaus mitä odottaa", "Eka raskaus", "ensiraskaus kokemus"],
    "parents_and_family": ["Isä", "Äiti", "Vanhemmat", "Vanhemmuus", "YH Äiti", "YH Isä", "Sukulaiset", "Isovanhemmat", "Isoäiti", "Isoisä", "Setä", "Eno", "Täti", "Kummi", "Parisuhde"],
    "society": ["Yhteiskunta", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä"],
    "health_issues": ["Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola"],
    "social_services": ["Sosiaalipalvelut", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku"]
}


def main():
    print("MAIN")
    conn = db.create_db("threads.db", reinit=False)

    unique_urls, details = gt.search(keywords=KEYWORDS["first_time_pregnancy"], conn=conn)
    # unique_urls, details = gt.search(["Ensimmäinen lapsi"], 0)
    timing.log("Thread URLs collected")
    log_search_details(details, st.TOTAL_REQUESTS)
    st.get_threads(unique_urls, conn)
    print(st.TOTAL_REQUESTS)
    db.close_connection(conn)
    return


def log_search_details(details, total_requests:int):
    with open("details.txt", "w+") as f:
        f.write(str(total_requests) + str(details))
    return


if __name__ == "__main__":
    try:
        main()
        print("DONE!")
    except KeyboardInterrupt:
        print("QUITTING...")
