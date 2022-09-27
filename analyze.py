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
from main import KEYWORDS
import timing

KEYWORDS = KEYWORDS
np.set_printoptions(threshold=sys.maxsize)


def main():
    threads = db.get_threads(conn, 'SELECT * FROM THREADS WHERE ANALYZE=1')

    support, votes, shares = test_strength(threads)

    # timing.log("Start plotting figures")
    # plot_strength(support)
    # plot_strength(votes, "support")

    timing.log("Constructing graph with threshold=2")
    G = construct_social_network_graph(threads, shares)
    # nx.write_gpickle(G,"garbo/pickled_graph")
    graph_attributes(G)
    graph_spectral_clustering(G)

    timing.log("Constructing graph with threshold=3")
    G3 = construct_social_network_graph(threads, shares, 3)
    graph_attributes(G3)
    graph_spectral_clustering(G3,3)

    timing.log("Constructing graph with threshold=4")
    G4 = construct_social_network_graph(threads, shares, 4)
    graph_attributes(G4)
    graph_spectral_clustering(G4,4)
    
    timing.log("Constructing graph with threshold=5")
    G5 = construct_social_network_graph(threads, shares, 5)
    graph_attributes(G5)
    graph_spectral_clustering(G5,5)

    return


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
    with open("figures/partition_quality" + str(th) + ".txt", "w") as f:
        f.write(tx)
    with open("figures/communities" + str(th) + ".txt", "w") as f:
        f.write(str(comstx))
    with open("figures/communities_lens" + str(th) + ".txt", "w") as f:
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

    plt.savefig("figures/graph" + str(threshold) + ".png", dpi="figure", format="png", transparent= False, bbox_inches="tight")
    plt.savefig("figures/graph_transparent" + str(threshold) + ".png", dpi="figure", format="png", transparent= True, bbox_inches="tight")

    return G


def graph_attributes(G:nx.Graph):
    timing.log("Start getting graph attributes")
    # Connected components
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    # Giant component
    G0 = G.subgraph(Gcc[0])

    # Number of nodes
    num_nodes = G.number_of_nodes()
    print("Nodes: ", num_nodes)

    # Number of edges
    num_edges = G.number_of_edges()
    print("Edges: ", num_edges)

    # Overall clustering coefficient
    clustering_coefficient = nx.average_clustering(G)
    print("Overall clustering coefficient: ", clustering_coefficient)

    # Size of giant component
    num_nodes_giant = G0.number_of_nodes()
    print("Giant component nodes: ", num_nodes_giant)

    # Number of edges
    num_edges_giant = G0.number_of_edges()
    print("Giant component edges: ", num_edges_giant)

    # diameter
    diameter = nx.diameter(G0)
    print("Diameter: ", diameter)

    # average degree centrality and its associated variance
    values = list(nx.degree_centrality(G).values())
    avg_degree_centrality = average(values)
    avg_degree_centrality_variance = np.var(values)
    print("average degree centrality: ", avg_degree_centrality,  ", it's associated variance: ", avg_degree_centrality_variance)

    # Average In-Betweeness centrality and its variance
    values = list(nx.betweenness_centrality(G).values())
    avg_betweenness_centrality = average(values)
    avg_betweenness_centrality_variance = np.var(values)
    print("Average In-Betweeness centrality: ", avg_betweenness_centrality, ", its variance: ", avg_betweenness_centrality_variance)
    
    # Average path length
    avg_path_length = nx.average_shortest_path_length(G0)
    print("Average path length: ", avg_path_length)

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
