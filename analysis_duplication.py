import argparse
import math
import sqlite3

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm


def load_graph(db, distances_path):
    conn = sqlite3.connect(db)
    query = f'SELECT id, local_path, user, repo FROM metamodels'
    df = pd.read_sql_query(query, conn)
    vertices = df.to_records(index=False).tolist()
    query = f'SELECT id, m1, m2 FROM duplicates'
    df = pd.read_sql_query(query, conn)

    df_distances = pd.read_csv(distances_path, names=['id', 'distance'], header=None)
    df = pd.merge(df, df_distances, on='id', how='inner')

    edges = df.to_records(index=False).tolist()

    G = nx.Graph()
    for x, local_path, user, repo in tqdm(vertices, desc='Adding nodes'):
        G.add_node(x, local_path=local_path, user=user, repo=repo)
    # add the edges to the graph
    for edge in tqdm(edges, desc='Adding edges'):
        if edge[1] not in G.nodes():
            continue
        if edge[2] not in G.nodes():
            continue
        G.add_edge(edge[1], edge[2], weight=edge[3])
    return G


def proportion(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    metrics_unique_repo = []
    metrics_unique_user = []
    for nodes in ccs:
        cluster_size = len(nodes)
        unique_repos = len(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in nodes]))
        metric = ((unique_repos - 1) / (cluster_size - 1)) * (
                math.log(cluster_size) / math.log(max([len(c) for c in ccs])))
        metrics_unique_repo.append(metric)

        unique_users = len(set([G.nodes[n]['user'] for n in nodes]))
        metric = (unique_users - 1) / (cluster_size - 1)
        metrics_unique_user.append(metric)

    plt.hist(metrics_unique_repo, edgecolor='black')

    # Adding titles and labels
    plt.title('Histogram of Sample Data')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

    metrics_unique_repo = np.asarray(metrics_unique_repo)
    lens = np.asarray([len(c) for c in ccs])

    print(lens[metrics_unique_repo >= .3])
    print(np.mean(lens[metrics_unique_repo >= .3]))
    print(np.std(lens[metrics_unique_repo >= .3]))


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


def intra_project_reuse(G):
    repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    result = {}
    scores = []
    files = {}
    diameters = []
    for repo in tqdm(repos, total=len(repos)):
        view = nx.subgraph_view(G, filter_node=lambda n: G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo)
        ccs = [c for c in list(sorted(nx.connected_components(view), key=len, reverse=True))]
        score = sum([len(c) - 1 for c in ccs])
        result[repo] = score
        files[repo] = [G.nodes[n]['local_path'] for c in ccs for n in c if len(ccs) > 1]
        scores.append(score)
        if len(view.edges) >= 0:
            ws = [data['weight'] for _, _, data in view.edges(data=True) if data['weight'] != -1]
            if len(ws) == 0:
                continue
            diameters.append(np.max(ws))

    print(f'Proportion intra {len([s for s in scores if s > 0]) / len(scores):.4f}')

    top_k = sorted(result, key=result.get, reverse=True)[:10]
    print(top_k)
    for r in top_k:
        print(r)
        print(files[r])

    plt.boxplot(diameters)

    # Adding titles and labels
    plt.title('Histogram of Sample Data')
    plt.xlabel('Diameter')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.show()


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


def test_models(G):
    tests = [n for n in G if 'test' in G.nodes[n]['local_path'] and G.edges(n)]
    all = [n for n in G if G.edges(n)]
    print(f'Proportion tests {len(tests) / len(all):.4f}')


def get_repos_datasets(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    result = {}
    for repo in tqdm(repos, total=len(repos)):
        cont = 0
        for c in ccs:
            intersect = [n for n in c if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo]
            if intersect:
                cont += 1
        result[repo] = cont

    top_k = sorted(result, key=result.get, reverse=True)[:10]
    print(top_k)
    for r in top_k:
        print(r, result[r])


def main(args):
    G = load_graph(args.db, args.distances)
    most_reused(G, 20)
    # proportion(G)
    # intra_project_reuse(G)
    get_repos_datasets(G)
    distances_inter_vs_intra(G)
    test_models(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    parser.add_argument('--distances', type=str, default='distances_all.csv')
    args = parser.parse_args()
    main(args)
