import argparse
import math
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from plotnine import *
from tqdm import tqdm

from analysis_duplication import load_graph
from analysis_intra import calculate_sample_size

random.seed(123)


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

    # proportion of repositories that copy metamodels from other repositories
    repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    cont = 0
    repos_inter = []
    for repo in tqdm(repos):
        nodes = [n for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo]
        for n in nodes:
            neig = [m for m in nx.neighbors(G, n) if G.nodes[m]['user'] + '/' + G.nodes[m]['repo'] != repo]
            if len(neig) > 0:
                cont += 1
                repos_inter.append(repo)
                break
    repos_inter = list(set(repos_inter))
    print(f'Proportion inter (repositories that copy metamodels from other repositories) {cont / len(repos):.4f}')
    print(f'Number of inter {cont} out of {len(repos)}')

    nodes_inter = []
    for r in tqdm(repos_inter):
        nodes = [n for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == r]
        node_inter = 0
        for n in nodes:
            neig = [m for m in nx.neighbors(G, n) if G.nodes[m]['user'] + '/' + G.nodes[m]['repo'] != r]
            if len(neig) > 0:
                node_inter += 1
        nodes_inter.append(node_inter / len(nodes))
    print(f'Mean proportion of inter-metamodels per repository: {np.mean(nodes_inter):.4f} +- {np.std(nodes_inter):.4f}')

    # blox-plot scores
    data = pd.DataFrame({'st1': nodes_inter})

    # Create the plot
    plot = (
            ggplot(data, aes(y='st1')) +  # Use 'y' for horizontal boxplot
            geom_boxplot() +
            # scale_y_log10() +  # Log scale for x-axis
            labs(
                title='Distribution of $InterDup\mathcal{M}_r$',
                y='$InterDup\mathcal{M}_r$',
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

    plot.save("inter_st1.pdf", format="pdf")





def sample_inter(G):
    repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    repos_inter = []
    for repo in tqdm(repos):
        nodes = [n for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo]
        for n in nodes:
            neig = [m for m in nx.neighbors(G, n) if G.nodes[m]['user'] + '/' + G.nodes[m]['repo'] != repo]
            if len(neig) > 0:
                repos_inter.append(repo)
                break
    repos_inter = list(set(repos_inter))
    print(f'Repos with inter-metamodels: {len(repos_inter)}')

    ccs = [[n for n in sorted(c, key=lambda x: G.nodes[x]['first_commit'])] for c in
           list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    first_commit_metamodels = [c[0] for c in ccs]

    population = []
    for repo in repos_inter:
        nodes = [n for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo]
        for n in nodes:
            if n in set(first_commit_metamodels):
                continue
            neig = [m for m in nx.neighbors(G, n) if G.nodes[m]['user'] + '/' + G.nodes[m]['repo'] != repo]
            neig = [m for m in neig if m in set(first_commit_metamodels)]
            if len(neig) > 0:
                assert len(neig) == 1
                population.append(repo)
                break
            else:
                continue

    print(f'Population size: {len(population)}')
    k = calculate_sample_size(len(population), 1.96, 0.5, 0.05)
    print(f'Sample size: {k}')
    sample = random.sample(population, k)

    metamodels = []
    originals = []
    originals_links = []
    for repo in sample:
        nodes = [n for n in G if G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo]
        metamodels_repo = []
        originals_repo = []
        originals_repo_links = []
        for n in nodes:
            if n in set(first_commit_metamodels):
                continue
            neig = [m for m in nx.neighbors(G, n) if G.nodes[m]['user'] + '/' + G.nodes[m]['repo'] != repo]
            neig = [m for m in neig if m in set(first_commit_metamodels)]
            if len(neig) > 0:
                assert len(neig) == 1
                original = neig[0]
                originals_repo.append(G.nodes[original]['local_path'])
                originals_repo_links.append('https://github.com/' +
                                            G.nodes[original]['user'] + '/' + G.nodes[original]['repo'])
                metamodels_repo.append(G.nodes[n]['local_path'])

        metamodels.append(' || '.join(metamodels_repo))
        originals.append(' || '.join(originals_repo))
        originals_links.append(' || '.join(originals_repo_links))


    df = pd.DataFrame({'repo': ['https://github.com/' + s for s in sample],
                       'metamodels': metamodels, 'originals': originals,
                       'originals_links': originals_links})
    df.to_csv('samples_inter.csv', index=False)

def histogram(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    len_ccs = [len(set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in c])) for c in ccs]
    len_css = [l for l in len_ccs if l > 1]

    plt.hist(len_ccs, bins=200, edgecolor='black')
    plt.yscale('log')

    # Adding titles and labels
    plt.title('Unique repository histogram')
    plt.xlabel('Unique repositories')
    plt.ylabel('Frequency')

    plt.savefig("histogram_inter.pdf", format="pdf")

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


def main(args):
    random.seed(123)
    G = load_graph(args.db)
    # histogram(G)
    amount_inter(G)
    # distances_inter_vs_intra(G)
    # normalized_scores(G)
    if args.sample:
        sample_inter(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    parser.add_argument('--sample', help='Remove duplicate models', action='store_true')
    args = parser.parse_args()
    main(args)
