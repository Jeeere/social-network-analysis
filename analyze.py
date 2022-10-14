"""
Analyzes collected threads
"""
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from cdlib import algorithms
from cdlib import NodeClustering
from sklearn import cluster
import sys
from networkx.algorithms import community

import database as db
# from main import KEYWORDS
import timing

KEYWORDSSS: dict = {
    "first_time_pregnancy": ["raskaus puudutus", "Ensimmäinen lapsi", "Ensimmäinen raskaus", "Ensikertalainen raskaus", "Äitiys", "Ensiraskaus Oireet", "Ensiraskaus", "Ensiraskaus vinkkejä", "Ensiraskaus mitä odottaa", "Eka raskaus", "ensiraskaus kokemus", "jälkeiset", "vauvakuume", "ympärileikkaus", "sikiö", "raskaus", "Gynekologi raskaus", "kätilö raskaus", "Keskenmeno", "Ovulaatio raskaus", "Istukka", "Kuolleena syntymä", "kohtu", "vagina raskaus"],
    "parents_and_family": ["adoptioisä", "lapsi", "vauva", "isäntä", "emäntä", "adoptioäiti", "esi-isä", "täti", "verisukulainen", "morsian", "sulhanen", "veli", "lanko", "veljeskunta", "veljellinen", "huoltaja", "lapsi", "lapsuus", "lapset", "serkku", "isä", "isi", "iskä", "isukki", "tytär", "miniä", "jälkeläinen", "avioero", "kihloissa", "ex", "entinen vaimo", "entinen mies", "suku", "perhe", "sukupuu", "appiukko", "morsian", "esikoinen", "kasvattilapsi", "sijaisisä", "sijaisäiti", "sijaisvanhempi", "veljellinen", "ystävä", "pappa", "paappa", "vaari", "ukki", "lapsenlapsi", "lapsenlapset", "tyttärentytär", "isoisä", "mummo", "mummu", "isoäiti", "isotäti", "lapsenlapsentytär", "isoisoisä", "isoisoäiti", "pojanpojanpoika", "isosetä", "sulhanen", "velipuoli", "siskopuoli", "perillinen", "perijätär", "perinnöllinen", "perintö", "aviomies", "identtinen kaksonen", "identtiset kaksoset", "appi", "sukulaiset", "sukulaisia", "sukulaisuus", "tyttönimi", "avioliitto", "äidin", "isän", "isin", "mamma", "isukin", "alaikäinen", "anoppi", "nana", "synnytys", "veljenpoika", "vastanainut", "veljentytär", "ydinperhe", "jälkeläisiä", "papa", "vanhempi", "kumppani", "jälkeläiset", "jälkeläisiä", "neloset", "pikkuserkku", "sisarus", "sisko", "käly", "sisaruus", "sisarellinen", "poika", "vävy", "puoliso", "velipuoli", "lapsipuoli", "lapsipuolet", "lapsipuolia", "isäpuoli", "äitipuoli", "poikapuoli", "kolmoset", "kaksoisveli", "kaksoissisko", "kaksoset", "setä", "yksinhuoltaja", "yh äiti", "yh isä"],
    "society": ["Yhteiskunta", "armeija", "väkijoukko", "KELA", "Tuki", "Tuet", "Äitiysvapaa", "Vanhempainvapaa", "Lapsilisä", "Inhimillinen yhteiskunta", "yhteiskunnalle", "yhteiskuntaan", "vapaaehtoinen", "yhteisö", "suvaitsevaisuus", "suvaitseva", "koulutus", "elinajanodote", "sukupolvien välinen kuilu", "sukupolvi", "yhteinen etu", "tuloero", "syrjintä", "rasismi", "eriarvoisuus", "syrjiä", "yhteinen hyvä", "yhteisen edun", "yhteisen hyvän", "suvaitsevaisuutta", "yhteisöllisyys", "yhteisössä", "vapaaehtoistyö", "oikeus", "viranomainen", "viranomaiset"],
    "health_issues": ["pahoinvoinnista ", "oksentamisesta ", "oireyhtymä", "Terveys", "Sairaus", "Sairaudet", "Lääkkeet", "Lääkäri", "Sairaanhoito", "Sairaala", "Neuvola", "allergia", "astma", "selkäkipu", "murtunut", "murtuma", "syöpä", "vilustunut", "flunssa", "vilustuminen", "yskä", "ripuli", "korvakipu", "kuume", "influenssa", "pääkipu", "päänsärky", "närästys", "närästää", "tuhkarokko", "vesirokko", "ihottuma", "kurkkukipu", "kipeä kurkku", "venähdys", "venähtänyt", "mahakipu", "vatsakipu", "hammaskipu", "auringonpolttama", "sairas", "kipeä", "kipu", "paha olo", "epidemia", "korona", "pandemia", "rutto"],
    "social_services": ["Sosiaalipalvelu", "lapsilisä", "Sosiaalituki", "Sossu", "KELA", "Neuvola", "Tuet", "Tuki", "kansaneläkelaitos", "syrjäytyminen", "syrjäytyä", "kriisi", "väkivalta", "kaltoinkohtelu", "hyvinvointi", "päihde", "päihteet", "mielenterveys", "sairaus", "vamma", "ikääntyminen", "läheinen", "läheisten", "läheisen", "omainen", "omaisen", "omaisten", "sosiaalityö", "sosiaaliohjaus", "kuntoutus", "perhetyö", "kotipalvelu", "kotihoito", "omaishoito", "asumispalvelu", "laitospalvelu", "mielenterveystyö", "päihdetyö", "kasvatusneuvonta", "perheneuvonta", "tapaamisen valvonta", "tapaamisten valvonta", "lapsi", "vanhempi", "omaishoidon tuki", "vammaispalvelu", "terveyspalvelu", "erityispalvelu", "sosiaalihuolto", "viranomainen", "sosiaaliministeriö", "terveysministeriö", "terveydenhuolto"],
    "finance_and_wealth": ["Raha", "Talous", "Palkka", "Äitiysraha", "Isyysraha", "Velka", "Laina", "Lasku", "korko", "vuosikorko", "omaisuus", "konkurssi", "budjetti", "vertailuostos", "vertailuostokset", "luotto", "luottoraportti", "luottopisteet", "luottokyky", "pankkikortti", "pankki", "luottokortti", "monipuolistaminen", "hajautus", "hajauttaa", "hätärahasto", "tulot", "lainanantaja", "kulu", "maksaa", "maksoi", "finanssit", "rahatalous", "omaisuutta", "pääoma", "onni", "rikas", "rikkauksia", "rikkaudet", "arvo", "arvoinen", "euro", "dollari", "kruunu", "markka", "punta", "rupla", "valuutta", "säästöt", "pesämuna", "valtionkassa", "lompakko", "henkilökohtainen omaisuus", "velat", "velkaantua", "velkaantuneisuus"]
}
np.set_printoptions(threshold=sys.maxsize)


def main():
    threads = db.get_threads(conn, 'SELECT * FROM THREADS WHERE ANALYZE=1')

    new_keywords = check_keywords(KEYWORDSSS)
    support, votes, shares = test_strength(threads,new_keywords)
    print(shares)
    for v in shares.values():
        print(len(v))

    # timing.log("Start plotting figures")
    # plot_strength(support)
    # plot_strength(votes, "support")

    timing.log("Constructing graph with threshold=2")
    G = construct_social_network_graph(threads, shares)
    # nx.write_gpickle(G,"garbo/pickled_graph")
    graph_attributes(G,2)
    graph_spectral_clustering(G)

    timing.log("Constructing graph with threshold=3")
    G3 = construct_social_network_graph(threads, shares, 3)
    graph_attributes(G3,3)
    graph_spectral_clustering(G3,3)

    timing.log("Constructing graph with threshold=4")
    G4 = construct_social_network_graph(threads, shares, 4)
    graph_attributes(G4,4)
    graph_spectral_clustering(G4,4)
    
    timing.log("Constructing graph with threshold=5")
    G5 = construct_social_network_graph(threads, shares, 5)
    graph_attributes(G5,5)
    graph_spectral_clustering(G5,5)

    return


def check_keywords(keywords:dict):
    """
    Removes duplicates from keywords
    """
    new_keywords = {
        "first_time_pregnancy": [],
        "parents_and_family": [],
        "society": [],
        "health_issues": [],
        "social_services": [],
        "finance_and_wealth": []
    }
    detected = []

    for category, words in keywords.items():
        for word in words:
            if word not in detected:
                detected.append(word)
                new_keywords[category].append(word)
            else:
                print(word)

    return new_keywords


def graph_spectral_clustering(G:nx.Graph, th:int=2):
    print("Entering community detection...")

    coms = community.girvan_newman(G)
    # coms = tuple(sorted(c) for c in next(comp))
    print("    Communities detected! Quantifying quality...")
    # Get coverage and performance
    tx = ""
    comstx = ""
    comslens = ""
    for com in coms:
        cov_per = nx.algorithms.community.partition_quality(G, com)
        tx += str(cov_per) + "\n"
        comstx += str(com) + "\n"
        comslens += str(len(com)) + "\n"
    with open("data/partition_quality" + str(th) + ".txt", "w") as f:
        f.write(tx)
    with open("data/communities" + str(th) + ".txt", "w") as f:
        f.write(str(comstx))
    with open("data/communities_lens" + str(th) + ".txt", "w") as f:
        f.write(str(comslens))
    return


def construct_social_network_graph(threads:list, shares:dict, threshold:int=2):
    """
    Creates a social network graph and saves it.\n
    Arguments:
        threads: list of threads from database
        shares: dictionary depicting which threads belong to which categories
    """
    print("Constructing social network graph with threshold=" + str(threshold) + "...")
    urls = [item[0] for item in threads]
    G = nx.Graph()
    G.add_nodes_from(urls)

    edges = check_edges(urls, shares, threshold)
    G.add_edges_from(edges)

    plt.subplots(figsize=(50,50))
    nx.draw_circular(G)

    plt.savefig("data/graph" + str(threshold) + ".png", dpi="figure", format="png", transparent= False, bbox_inches="tight")
    plt.savefig("data/graph_transparent" + str(threshold) + ".png", dpi="figure", format="png", transparent= True, bbox_inches="tight")

    return G


def graph_attributes(G:nx.Graph, num:int):
    txt = ""
    timing.log("Start getting graph attributes")
    # Connected components
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    # Giant component
    G0 = G.subgraph(Gcc[0])

    # Number of nodes
    num_nodes = G.number_of_nodes()
    p = "Nodes: " + str(num_nodes)
    print(p)
    txt += p + "\n"

    # Number of edges
    num_edges = G.number_of_edges()
    p = "Edges: " + str(num_edges)
    print(p)
    txt += p + "\n"

    # Overall clustering coefficient
    clustering_coefficient = nx.average_clustering(G)
    p = "Overall clustering coefficient: " + str(clustering_coefficient)
    print(p)
    txt += p + "\n"

    # Size of giant component
    num_nodes_giant = G0.number_of_nodes()
    p = "Giant component nodes: " + str(num_nodes_giant)
    print(p)
    txt += p + "\n"

    # Number of edges
    num_edges_giant = G0.number_of_edges()
    p = "Giant component edges: " + str(num_edges_giant)
    print(p)
    txt += p + "\n"

    # diameter
    diameter = nx.diameter(G0)
    p = "Diameter: " + str(diameter)
    print(p)
    txt += p + "\n"

    # average degree centrality and its associated variance
    values = list(nx.degree_centrality(G).values())
    avg_degree_centrality = average(values)
    avg_degree_centrality_variance = np.var(values)
    p = "average degree centrality: " + str(avg_degree_centrality) + ", it's associated variance: " + str(avg_degree_centrality_variance)
    print(p)
    txt += p + "\n"

    # Average In-Betweeness centrality and its variance
    values = list(nx.betweenness_centrality(G).values())
    avg_betweenness_centrality = average(values)
    avg_betweenness_centrality_variance = np.var(values)
    p = "Average In-Betweeness centrality: " + str(avg_betweenness_centrality) + ", its variance: " + str(avg_betweenness_centrality_variance)
    print(p)
    txt += p + "\n"
    
    # Average path length
    avg_path_length = nx.average_shortest_path_length(G0)
    p = "Average path length: " + str(avg_path_length)
    print(p)
    txt += p + "\n"

    with open("data/attributes" + str(num) + ".txt", "w") as f:
        f.write(txt)

    return


def average(values:list):
    return sum(values) / len(values)


def check_edges(all_threads:list, by_cat:dict, threshold:int=2):
    """
    Checks for possible edges between all nodes.\n
    Arguments:
        all_threads: list of all thread URLs
        by_cat: dictionary depicting which threads belong to which categories
        threshold: minimum number of categories in common for two nodes to make an edge
    Returns:
        edges: list of edges
    """
    print("Checking for edges...")
    edges =[]
    # pairs = [(all_threads[i],all_threads[j]) for i in range(len(all_threads)) for j in range(i+1, len(all_threads))]
    pairs = []

    # Create unique pairs of threads
    for i in range(len(all_threads)):
        for j in all_threads[i+1:]:
            if all_threads[i] == j:
                continue
            else:
                pairs.append((all_threads[i],j))

    while len(pairs) > 0:
        check, next = pairs.pop(0)
        
        share = 0
        for category, threads in by_cat.items():
            if(check in threads and next in threads):
                share += 1
            if share >= threshold:
                edges.append((check, next))
                break

    return edges


def test_strength(threads:list, keywords):
    """
    Tests strength of each category with a simple string matching of the keyword lists.\n
    Arguments:
        threads: list of threads to be tested.
    """
    timing.log("Start testing strength")
    print("Testing strength...")
    
    cat_strength = {
            "parents_and_family": 0,
            "society": 0,
            "health_issues": 0,
            "social_services": 0,
            "finance_and_wealth": 0
            }
    cat_votes = {
            "parents_and_family": 0,
            "society": 0,
            "health_issues": 0,
            "social_services": 0,
            "finance_and_wealth": 0
            }
    cat_threads = {
            "parents_and_family": [],
            "society": [],
            "health_issues": [],
            "social_services": [],
            "finance_and_wealth": []
            }

    for thread in threads:
        thread_json = json.loads(thread[5].replace("'", '"'))
 
        for reply_num, data in thread_json.items():
            # Test parents and family
            cat_strength, cat_votes, cat_threads = thing("parents_and_family",cat_strength,cat_votes,cat_threads,data,thread,keywords)
            # Test society
            cat_strength, cat_votes, cat_threads = thing("society",cat_strength,cat_votes,cat_threads,data,thread,keywords)
            # Test health issues
            cat_strength, cat_votes, cat_threads = thing("health_issues",cat_strength,cat_votes,cat_threads,data,thread,keywords)
            # Test social services
            cat_strength, cat_votes, cat_threads = thing("social_services",cat_strength,cat_votes,cat_threads,data,thread,keywords)
            # Test finance and wealth
            cat_strength, cat_votes, cat_threads = thing("finance_and_wealth",cat_strength,cat_votes,cat_threads,data,thread,keywords)

    return cat_strength, cat_votes, cat_threads


def thing(category:str, cat_strength:dict, cat_votes:dict, threads_by_cat:dict, data, thread, keywords):
    """
    Updates category stats if thread belongs to category
    """
    cat_support = test_category_support(category, data, thread,keywords)
    
    if(cat_support > 0):
        cat_votes[category] = cat_votes[category] + data["likes"] + data["dislikes"]
        cat_strength[category] = cat_strength[category] + cat_support
    

    if(cat_support>0 and thread[0] not in threads_by_cat[category]):
        threads_by_cat[category].append(thread[0])
    
    return cat_strength, cat_votes, threads_by_cat


def plot_strength(support, filename:str="strengths"):
    """
    Traces a bar plot showing the proportion of each category in the collected database.
    """
    print("Plotting "+filename+"...")
    values = list(support.values())
    width = 0.3

    fig, ax = plt.subplots(figsize=(9,6))
    ax.bar(list(support.keys()), values, width)
    for i, v in enumerate(values):
        ax.text(i - .15, v + 1000, str(v))
    plt.savefig("data/" + filename + "_transparent.png", dpi= "figure", format= "png", transparent= True)
    plt.savefig("data/" + filename + ".png", dpi= "figure", format= "png", transparent= False)

    return


def test_category_support(category:str, message:str, thread, keywords):
    """
    Counts how many times keywords of a given category appear in a message
    """
    support = 0
    tested = []
    for keyword in keywords[category]:
        if keyword not in tested:
            support += message["text"].count(keyword)
            tested.append(keyword)

    return support


if __name__ == "__main__":
    try:
        global conn
        conn = db.create_db_connection("data/threads.db")
        main()
        print("QUITTING...")
    except KeyboardInterrupt:
        print("QUITTING...")
    db.close_connection(conn)
