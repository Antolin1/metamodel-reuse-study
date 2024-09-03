import argparse
import math
import sqlite3

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
    query = f'SELECT id, m1, m2, distance FROM duplicates where distance != -1'
    df = pd.read_sql_query(query, conn)
    edges = df.to_records(index=False).tolist()

    G = nx.Graph()
    for x, local_path, user, repo, first_commit in tqdm(vertices, desc='Adding nodes'):
        G.add_node(x, local_path=local_path, user=user, repo=repo, first_commit=first_commit)
    # add the edges to the graph
    for edge in tqdm(edges, desc='Adding edges'):
        if edge[1] not in G.nodes():
            continue
        if edge[2] not in G.nodes():
            continue
        G.add_edge(edge[1], edge[2], weight=edge[3])
    return G


def most_reused(G, k=10):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    print(f'Number connected components > 1: {len(ccs)}')
    for j, c in enumerate(ccs[0:k]):
        c = [G.nodes[n]['local_path'] for n in c]
        print(f'Top {j + 1}, Components {len(c)}')
        print(c[0:10])

    len_ccs = [len(c) for c in ccs]
    plt.hist(len_ccs, bins=300, edgecolor='black')
    plt.yscale('log')

    # Adding titles and labels
    plt.title('Histogram of Sample Data')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

    # Display the plot
    plt.show()


def amount_duplication(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    print(f"Duplicated files: {100 * sum([len(c) for c in ccs]) / len(G):.2f}")


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

    amount_duplication(G)
    most_reused(G, 10)
    compactness(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
