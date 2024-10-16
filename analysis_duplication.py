import argparse
import math
import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm


def load_graph(db):
    conn = sqlite3.connect(db)
    query = f'SELECT id, local_path, user, repo, first_commit FROM metamodels'
    df = pd.read_sql_query(query, conn)
    vertices = df.to_records(index=False).tolist()
    query = f'SELECT id, m1, m2, distance FROM duplicates'
    df = pd.read_sql_query(query, conn)
    edges = df.to_records(index=False).tolist()

    G = nx.Graph()
    for x, local_path, user, repo, first_commit in tqdm(vertices, desc='Adding nodes'):
        G.add_node(x, local_path=local_path, user=user, repo=repo, first_commit=datetime.strptime(first_commit,
                                                                                                  "%Y-%m-%d %H:%M:%S%z"))
    # add the edges to the graph
    for edge in tqdm(edges, desc='Adding edges'):
        if edge[1] not in G.nodes():
            continue
        if edge[2] not in G.nodes():
            continue
        G.add_edge(edge[1], edge[2], weight=edge[3])
    return G

def get_unique_repos(G, c):
    return len(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in c]))


def histogram(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    len_ccs = [len(c) for c in ccs]
    plt.hist(len_ccs, bins=200, edgecolor='black')
    plt.yscale('log')

    # Adding titles and labels
    plt.title('Cluster sizes histogram')
    plt.xlabel('Cluster size')
    plt.ylabel('Frequency')

    plt.savefig("histogram.pdf", format="pdf")

    # Display the plot
    plt.show()

    # Step 1: Calculate the median of the data
    median = np.median(len_ccs)
    # Step 2: Calculate the absolute deviations from the median
    absolute_deviations = np.abs(len_ccs - median)
    # Step 3: Calculate the median of the absolute deviations (MAD)
    mad = np.median(absolute_deviations)
    print(f'Median cluster size: {median:.2f}')
    print(f'Median absolute deviation: {mad:.2f}')

def most_duplicated(G, k=10):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    for j, c in enumerate(ccs[0:k]):
        files = [G.nodes[n]['local_path'] for n in c]
        r = list(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in c]))
        print(f'Top {j + 1}, Components {len(c)}, Unique repos {len(r)}, Ratio {len(r) / len(c):.2f}')
        print(files)

    print('-----------------------------------')
    ccs = [c for c in list(sorted(nx.connected_components(G), key=lambda x: get_unique_repos(G, x),
                                  reverse=True)) if len(c) > 1]
    for j, c in enumerate(ccs[0:k]):
        files = [G.nodes[n]['local_path'] for n in c]
        r = list(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in c]))
        print(f'Top {j + 1}, Components {len(c)}, Unique repos {len(r)}, Ratio {len(r) / len(c):.2f}')
        print(files)



def statistics_amount_duplication(G):

    # count the number of nodes that have at least one edge divided by the total number of nodes
    print(f"Duplicated files: {100 * len([n for n in G.nodes() if G.degree(n) > 0]) / len(G):.2f}")

    # number of distinct meta-models
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True))]
    print(f"Number of distinct meta-models: {len(ccs)}")

    # number of total files
    print(f"Number of total meta-models: {len(G)}")

    # ratio of distinct meta-models
    print(f"Ratio distinct meta-models: {100*len(ccs)/len(G):.2f}")



def compactness(G):
    weights = [data['weight'] for u, v, data in G.edges(data=True)]

    print(f'Mean weight: {np.mean(weights):.2f} +- {np.std(weights)}')
    print(f'Median weight: {np.median(weights):.2f}')

    plt.boxplot(weights)
    plt.yscale('log')

    # Adding titles and labels
    plt.title('Histogram of weights')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

    # Display the plot
    plt.show()


def main(args):
    G = load_graph(args.db)

    statistics_amount_duplication(G)
    histogram(G)
    most_duplicated(G)
    # compactness(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
