import argparse
import math
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from analysis_duplication import load_graph


def distances_inter_vs_intra(G):
    group_inter = [data['weight'] for x, y, data in G.edges(data=True) if data['weight'] != -1 and
                   (G.nodes[x]['user'] + '/' + G.nodes[x]['repo'] != G.nodes[y]['user'] + '/' + G.nodes[y]['repo'])]

    group_intra = [data['weight'] for x, y, data in G.edges(data=True) if data['weight'] != -1 and
                   (G.nodes[x]['user'] + '/' + G.nodes[x]['repo'] == G.nodes[y]['user'] + '/' + G.nodes[y]['repo'])]

    print(f'Group inter {len(group_inter)}, {np.mean(group_inter):.2f}, {np.median(group_inter)}')
    print(f'Group intra {len(group_intra)}, {np.mean(group_intra):.2f}, {np.median(group_intra)}')

    plt.boxplot([group_intra, group_inter], labels=['Intra', 'Inter'])

    # Adding title and labels
    plt.title('Boxplot inter vs intra')
    plt.xlabel('Group')
    plt.ylabel('Values')
    plt.yscale('log')
    # Show the plot
    plt.show()


def normalized_scores(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    metrics_unique_repo = []
    for nodes in ccs:
        cluster_size = len(nodes)
        unique_repos = len(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in nodes]))
        metric = ((unique_repos - 1) / (cluster_size - 1)) * (
                math.log(cluster_size) / math.log(max([len(c) for c in ccs])))
        metrics_unique_repo.append(metric)

    plt.hist(metrics_unique_repo, edgecolor='black')

    # Adding titles and labels
    plt.title('Histogram of Sample Data')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

    # metrics_unique_repo = np.asarray(metrics_unique_repo)
    # lens = np.asarray([len(c) for c in ccs])

    # print(lens[metrics_unique_repo >= .3])
    # print(np.mean(lens[metrics_unique_repo >= .3]))
    # print(np.std(lens[metrics_unique_repo >= .3]))


def amount_inter(G):
    cont = 0
    for n in G:
        for m in nx.neighbors(G, n):
            if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] !=  G.nodes[m]['user'] + '/' + G.nodes[m]['repo']:
                cont += 1
                break
    print(f'Proportion inter (metamodels that can be found in another repo) {cont / len(G):.4f}')


def main(args):
    random.seed(123)
    G = load_graph(args.db)
    amount_inter(G)
    distances_inter_vs_intra(G)
    normalized_scores(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
