import argparse
import sqlite3
from datetime import datetime

import networkx as nx
import numpy as np
import pandas as pd
from plotnine import *
from tqdm import tqdm


def load_graph(db):
    conn = sqlite3.connect(db)
    query = f'SELECT id, local_path, user, repo, first_commit FROM metamodels'
    df = pd.read_sql_query(query, conn)
    vertices = df.to_records(index=False).tolist()
    query = f'SELECT id, m1, m2 FROM duplicates'
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
        G.add_edge(edge[1], edge[2])
    return G

def get_unique_repos(G, c):
    return len(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in c]))


def histogram(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    len_ccs = [len(c) for c in ccs]
    data = pd.DataFrame({'ClusterSize': len_ccs})

    # Create the plot
    plot = (
            ggplot(data, aes(x='ClusterSize')) +
            geom_histogram(bins=200, color='black', fill='gray') +
            scale_y_log10() +
            labs(
                title='Cluster sizes distribution',
                x='Cluster size',
                y='Frequency'
            ) +
            theme_minimal()
            +
    theme(
        plot_title=element_text(size=16),  # Title font size
        axis_title_x=element_text(size=14),  # X-axis label font size
        axis_title_y=element_text(size=14),  # Y-axis label font size
        axis_text_x=element_text(size=12),  # X-axis tick font size
        axis_text_y=element_text(size=12)   # Y-axis tick font size
    )
    )

    # Save the plot as a PDF
    plot.save("histogram.pdf", format="pdf")

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
    print(f"Duplicated files (ST1): {100 * len([n for n in G.nodes() if G.degree(n) > 0]) / len(G):.2f}")

    # number of distinct meta-models
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True))]
    # print(f"Number of distinct meta-models: {len(ccs)}")

    # number of total files
    # print(f"Number of total meta-models: {len(G)}")

    # ratio of distinct meta-models
    print(f"Ratio distinct meta-models (ST2): {100*len(ccs)/len(G):.2f}")




def main(args):
    G = load_graph(args.db)
    statistics_amount_duplication(G)
    histogram(G)
    most_duplicated(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
