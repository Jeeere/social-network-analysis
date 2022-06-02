"""
Analyzes collected threads
"""
import json
import matplotlib.pyplot as plt
import networkx as nx

import database as db
from main import KEYWORDS
import timing

KEYWORDS = KEYWORDS


def main():
    threads = db.get_threads(conn, 'SELECT * FROM THREADS WHERE ANALYZE=1')

    timing.log("Start testing strength")
    support, votes, shares = test_strength(threads)

    timing.log("Start plotting figures")
    plot_strength(support)
    plot_strength(votes, "support")

    timing.log("Start constructing social network graph")
    construct_social_network_graph(threads, shares)

    return


def construct_social_network_graph(threads:list, shares:dict):
    """
    Creates a social network graph and saves it.\n
    Arguments:
        threads: list of threads from database
        shares: dictionary depicting which threads belong to which categories
    """
    print("Constructing social network graph...")
    urls = [item[0] for item in threads]
    G = nx.Graph()
    G.add_nodes_from(urls)

    edges = check_edges(urls, shares)

    G.add_edges_from(edges)
    print("Nodes: " + str(G.number_of_nodes()) + ", Edges: " + str(G.number_of_edges()))

    plt.subplots(figsize=(50,50))
    nx.draw_circular(G)

    plt.savefig("figures/graph.png", dpi= "figure", format= "png", transparent= False, bbox_inches="tight")
    plt.savefig("figures/graph_transparent.png", dpi= "figure", format= "png", transparent= True, bbox_inches="tight")

    return

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
    pairs = [(all_threads[i],all_threads[j]) for i in range(len(all_threads)) for j in range(i+1, len(all_threads))]

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


def test_strength(threads:list):
    """
    Tests strength of each category with a simple string matching of the keyword lists.\n
    Arguments:
        threads: list of threads to be tested.
    """
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
            cat_strength, cat_votes, cat_threads = thing("parents_and_family",cat_strength,cat_votes,cat_threads,data,thread)
            # Test society
            cat_strength, cat_votes, cat_threads = thing("society",cat_strength,cat_votes,cat_threads,data,thread)
            # Test health issues
            cat_strength, cat_votes, cat_threads = thing("health_issues",cat_strength,cat_votes,cat_threads,data,thread)
            # Test social services
            cat_strength, cat_votes, cat_threads = thing("social_services",cat_strength,cat_votes,cat_threads,data,thread)
            # Test finance and wealth
            cat_strength, cat_votes, cat_threads = thing("finance_and_wealth",cat_strength,cat_votes,cat_threads,data,thread)

    return cat_strength, cat_votes, cat_threads


def thing(category:str, cat_strength:dict, cat_votes:dict, threads_by_cat:dict, data, thread):
    """
    
    """
    cat_support = test_category_support(category, data, thread)
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
    plt.savefig("figures/" + filename + "_transparent.png", dpi= "figure", format= "png", transparent= True)
    plt.savefig("figures/" + filename + ".png", dpi= "figure", format= "png", transparent= False)

    return


def test_category_support(category:str, message:str, thread):
    """
    
    """
    support = 0
    tested = []
    for keyword in KEYWORDS[category]:
        if keyword not in tested:
            support += message["text"].count(keyword)
            tested.append(keyword)

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