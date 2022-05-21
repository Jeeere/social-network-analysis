import database as db
import get_threads as gt
import scrape_threads as st

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
    conn = db.create_db("threads.db")

    unique_urls = gt.search(KEYWORDS["first_time_pregnancy"])
    # unique_urls = gt.search(["Ensimmäinen lapsi"], 0)
    print("Number of unique threads collected: " + str(len(unique_urls)))
    st.get_threads(unique_urls, conn)

    db.close_connection(conn)
    return


if __name__ == "__main__":
    try:
        main()
        print("DONE!")
    except KeyboardInterrupt:
        print("QUITTING...")
