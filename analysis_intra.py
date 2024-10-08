import argparse
import json
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm

from analysis_duplication import load_graph


def calculate_sample_size(N, Z, P, E):
    """
    Calculate the required sample size for a finite population.

    Parameters:
    N (int): Population size
    Z (float): Z-score corresponding to the desired confidence level
    P (float): Estimated proportion (use 0.5 if unknown)
    E (float): Margin of error (expressed as a decimal; e.g., 0.05 for 5%)

    Returns:
    int: Required sample size
    """
    numerator = N * (Z ** 2) * P * (1 - P)
    denominator = (N - 1) * (E ** 2) + (Z ** 2) * P * (1 - P)

    return int(numerator / denominator)

def intra_project_reuse(G, args):
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
    print(f'Number repos {len(repos)}')

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
    if args.sample:
        repos_all = [r for r in result if result[r] > 0]
        k = calculate_sample_size(len(repos_all), 1.96, 0.5, 0.05)
        samples = random.sample(repos_all, k)
        sample_files = [json.dumps(files[s]) for s in samples]

        df = pd.DataFrame({'repos': samples, 'files': sample_files})
        df.to_csv('samples_intra.csv', index=False)

def main(args):
    random.seed(123)
    G = load_graph(args.db)
    # repos_with_dup = repos_with_duplication(G)

    intra_project_reuse(G, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    parser.add_argument('--sample', help='Remove duplicate models', action='store_true')
    args = parser.parse_args()
    main(args)
