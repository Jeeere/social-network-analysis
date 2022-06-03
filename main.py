import database as db
import get_threads as gt
import scrape_threads as st
import timing

KEYWORDS: dict = {
    "first_time_pregnancy": ["raskaus puudutus", "Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen raskaus", "Äitiys", "Ensiraskaus Oireet", "Ensiraskaus", "Ensiraskaus vinkkejä", "Ensiraskaus mitä odottaa", "Eka raskaus", "ensiraskaus kokemus", "jälkeiset", "vauvakuume", "ympärileikkaus", "sikiö", "raskaus", "Gynekologi raskaus", "kätilö raskaus", "Keskenmeno", "Ovulaatio raskaus", "Istukka", "Kuolleena syntymä", "kohtu", "vagina raskaus"],
    "parents_and_family": ["adoptioisä", "lapsi", "vauva", "isäntä", "emäntä", "adoptioäiti", "esi-isä", "täti", "verisukulainen", "morsian", "sulhanen", "veli", "lanko", "veljeskunta", "veljellinen", "huoltaja", "lapsi", "lapsuus", "lapset", "serkku", "isä", "isi", "iskä", "isukki", "tytär", "miniä", "jälkeläinen", "avioero", "kihloissa", "ex", "entinen vaimo", "entinen mies", "suku", "perhe", "sukupuu", "appiukko", "morsian", "esikoinen", "kasvattilapsi", "sijaisisä", "sijaisäiti", "sijaisvanhempi", "veljellinen", "ystävä", "sukututkimus", "pappa", "paappa", "vaari", "ukki", "lapsenlapsi", "lapsenlapset", "tyttärentytär", "isoisä", "mummo", "mummu", "isoäiti", "isotäti", "lapsenlapsentytär", "isoisoisä", "isoisoäiti", "pojanpojanpoika", "isosetä", "sulhanen", "velipuoli", "siskopuoli", "perillinen", "perijätär", "perinnöllinen", "perintö", "koti", "kotitalous", "aviomies", "identtinen kaksonen", "identtiset kaksoset", "appi", "taapero", "vauva", "periä", "perinnöstä", "nuori", "teini", "nuoriso", "sukulaiset", "sukulaisia", "sukulaisuus", "rakkaus", "uskollisuus", "tyttönimi", "avioliitto", "äidin", "isän", "isin", "mamma", "isukin", "matriarkka", "alaikäinen", "yksiavioisuus", "anoppi", "nana", "synnytys", "veljenpoika", "vastanainut", "veljentytär", "ydinperhe", "häät", "jälkeläisiä", "orpo", "papa", "vanhempi", "kumppani", "jälkeläiset", "jälkeläisiä", "neloset", "suhteet", "pikkuserkku", "sisarus", "sisko", "käly", "sisaruus", "sisarellinen", "poika", "vävy", "puoliso", "velipuoli", "lapsipuoli", "lapsipuolet", "lapsipuolia", "isäpuoli", "äitipuoli", "poikapuoli", "kolmoset", "kaksoisveli", "kaksoissisko", "kaksoset", "setä", "nuorukainen", "yksinhuoltaja", "yh äiti", "yh isä"],
    "society": ["Yhteiskunta", "armeija", "väkijoukko", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä", "Inhimillinen yhteiskunta", "yhteiskunnalle", "yhteiskuntaan", "persoonallisuus", "luonne", "itsevarma", "vapaaehtoinen", "yhteisö", "hyväksyttävä", "suvaitsevaisuus", "suvaitseva", "koulutus", "elinajanodote", "sukupolvien välinen kuilu", "sukupolvi", "yhteinen etu", "tuloero", "syrjintä", "rasismi", "eriarvoisuus", "syrjiä", "yhteinen hyvä", "yhteisen edun", "yhteisen hyvän", "kulutus", "kuluttaminen", "kuluttaa", "suvaitsevaisuutta", "yhteisöllisyys", "yhteisössä", "vapaaehtoistyö", "oikeus", "viranomainen", "viranomaiset"],
    "health_issues": ["pahoinvoinnista ", "oksentamisesta ", "oireyhtymä", "Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola", "allergia", "astma", "selkäkipu", "murtunut", "murtuma", "syöpä", "vilustunut", "flunssa", "vilustuminen", "yskä", "ripuli", "korvakipu", "kuume", "influenssa", "pääkipu", "päänsärky", "närästys", "närästää", "tuhkarokko", "vesirokko", "ihottuma", "kurkkukipu", "kipeä kurkku", "venähdys", "venähtänyt", "mahakipu", "vatsakipu", "hammaskipu", "auringonpolttama", "sairas", "kipeä", "kipu", "paha olo", "epidemia", "korona", "pandemia", "rutto"],
    "social_services": ["Sosiaalipalvelu", "lapsilisä", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki", "kansaneläkelaitos", "syrjäytyminen", "syrjäytyä", "kriisi", "väkivalta", "kaltoinkohtelu", "hyvinvointi", "päihde", "päihteet", "mielenterveys", "sairaus", "vamma", "ikääntyminen", "läheinen", "läheisten", "läheisen", "omainen", "omaisen", "omaisten", "sosiaalityö", "sosiaaliohjaus", "kuntoutus", "perhetyö", "kotipalvelu", "kotihoito", "omaishoito", "asumispalvelu", "laitospalvelu", "mielenterveystyö", "päihdetyö", "kasvatusneuvonta", "perheneuvonta", "tapaamisen valvonta", "tapaamisten valvonta", "lapsi", "vanhempi", "omaishoidon tuki", "vammaispalvelu", "terveyspalvelu", "erityispalvelu", "sosiaalihuolto", "viranomainen", "sosiaaliministeriö", "terveysministeriö", "terveydenhuolto"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku", "korko", "vuosikorko", "omaisuus", "konkurssi", "budjetti", "vertailuostos", "vertailuostokset", "luotto", "luottoraportti", "luottopisteet", "luottokyky", "pankkikortti", "pankki", "luottokortti", "monipuolistaminen", "hajautus", "hajauttaa", "hätärahasto", "tulot", "lainanantaja", "kulu", "maksaa", "maksoi", "finanssit", "rahatalous", "omaisuutta", "pääoma", "onni", "rikas", "rikkauksia", "rikkaudet", "arvo", "arvoinen", "euro", "dollari", "kruunu", "markka", "punta", "rupla", "valuutta", "säästöt", "pesämuna", "valtionkassa", "lompakko", "henkilökohtainen omaisuus", "velat", "velkaantua", "velkaantuneisuus"]
}


def main():
    print("MAIN")
    global conn
    conn = db.create_db("threads.db", reinit=False)

    unique_urls, details = gt.search(keywords=KEYWORDS["first_time_pregnancy"], conn=conn)
    # unique_urls, details = gt.search(["raskaus puudutus"], conn=conn, last_page=0)
    timing.log("Thread URLs collected")
    log_search_details(details, st.TOTAL_REQUESTS)
    st.get_threads(unique_urls, conn)
    print(st.TOTAL_REQUESTS)
    
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
    db.close_connection(conn)
