import argparse
import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm

from analysis_duplication import load_graph


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
        files[repo] = [[G.nodes[n]['local_path'] for n in c] for c in ccs if len(c) > 1]
        scores.append(score)
        if len(view.edges) >= 0:
            ws = [data['weight'] for _, _, data in view.edges(data=True) if data['weight'] != -1]
            if len(ws) == 0:
                continue
            diameters += ws

    print(f'Proportion intra (repos that contain duplication) {len([s for s in scores if s > 0]) / len(scores):.4f}')
    print(f'Number repos intra {len([s for s in scores if s > 0])}')

    plt.boxplot(diameters)

    # Adding titles and labels
    plt.title('Histogram of Sample Data')
    plt.xlabel('Diameter')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.show()

    print(f'Mean diameter: {np.mean(diameters):.2f} +- {np.std(diameters)}')
    print(f'Median diameter: {np.median(diameters):.2f}')

    # sample repos
    repos_all = [r for r in result if result[r] > 0]
    samples = random.sample(repos_all, 100)
    sample_files = [json.dumps(files[s]) for s in samples]

    df = pd.DataFrame({'repos': samples, 'files': sample_files})
    df.to_csv('samples_intra.csv', index=False)


def main(args):
    random.seed(123)
    G = load_graph(args.db)
    intra_project_reuse(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
