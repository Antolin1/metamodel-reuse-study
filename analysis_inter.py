import argparse
import math
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

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
            if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] != G.nodes[m]['user'] + '/' + G.nodes[m]['repo']:
                cont += 1
                break
    print(f'Proportion inter (metamodels that can be found in another repo) {cont / len(G):.4f}')


def sample_inter(G):
    # when sampling exclude the first since it could potentially be the first meta-model
    # todo: consider sampling repositories not meta-models. It could happen that in a cluster, all models come from
    # the same repository. Sample, for each cluster, one repository that is not the first one?
    # compute repositories that borrow meta-models from other repos
    ccs = [[n for n in sorted(c, key=lambda x: G.nodes[x]['first_commit'])] for c in
           list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    cluster = {x: y for x, y in enumerate(ccs)}
    dict_cluster = {y: x for x, a in enumerate(ccs) for y in a}

    population = list(
        set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for c in ccs for n in c if G.nodes[n]['user'] + '/' +
             G.nodes[n]['repo'] != G.nodes[c[0]]['user'] + '/' + G.nodes[c[0]]['repo']]))
    # print([G.nodes[n]['first_commit'] for n in ccs[0]])

    repos = random.sample(population, 100)

    def has_edge_other(G, n):
        repo = G.nodes[n]['user'] + '/' + G.nodes[n]['repo']
        for m in G.neighbors(n):
            if repo != G.nodes[m]['user'] + '/' + G.nodes[m]['repo']:
                return True
        return False

    metamodels = [[G.nodes[n]['local_path'] for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == r
                   and has_edge_other(G, n)]
                  for r in repos]
    originals = [[G.nodes[cluster[dict_cluster[n]][0]]['local_path'] for n in G if
                  G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == r
                  and has_edge_other(G, n)]
                 for r in repos]

    df = pd.DataFrame({'repo': repos, 'metamodel': metamodels, 'original': originals})
    df.to_csv('samples_inter.csv', index=False)


def main(args):
    random.seed(123)
    G = load_graph(args.db)
    amount_inter(G)
    distances_inter_vs_intra(G)
    normalized_scores(G)
    sample_inter(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
