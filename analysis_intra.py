import argparse
import json
import random

import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm
from plotnine import *

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
    st1 = []
    num_files = []
    duplicated_files = []
    for repo in tqdm(repos, total=len(repos)):
        view = nx.subgraph_view(G, filter_node=lambda n: G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo)
        ccs = [c for c in list(sorted(nx.connected_components(view), key=len, reverse=True))]
        score = sum([len(c) - 1 for c in ccs])
        result[repo] = score
        if score > 0:
            st1.append(100*len([n for n in view.nodes() if view.degree(n) > 0]) / len(view))
            num_files.append(len(view.nodes()))
            duplicated_files.append(len([n for n in view.nodes() if view.degree(n) > 0]))
        files[repo] = [[G.nodes[n]['local_path'] for n in c] for c in ccs if len(c) > 1]
        scores.append(score)

    print(f'Proportion intra (repos that contain duplication) {len([s for s in scores if s > 0]) / len(scores):.4f}')
    print(f'Number repos intra {len([s for s in scores if s > 0])}')
    print(f'Number repos {len(repos)}')

    # blox-plot scores
    data = pd.DataFrame({'st1': st1})

    # Create the plot
    plot = (
            ggplot(data, aes(y='st1')) +  # Use 'y' for horizontal boxplot
            geom_boxplot() +
            # scale_y_log10() +  # Log scale for x-axis
            labs(
                title='Distribution of $Dup\mathcal{M}_r$',
                y='$Dup\mathcal{M}_r$',
                x=''  # No y-axis label since it's horizontal
            ) +
            theme_minimal() +
            theme(
                plot_title=element_text(size=16),  # Title font size
                axis_title_x=element_text(size=14),  # X-axis label font size
                axis_text_y=element_blank()
            )
            + coord_flip()
    )

    plot.save("intra_st1.pdf", format="pdf")


    print(f'Mean score ST1: {np.mean(st1):.2f} +- {np.std(st1)}')
    print(f'Median score ST1: {np.median(st1):.2f}')


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
