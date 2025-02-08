import json
import random

import networkx as nx
import pandas as pd
from tqdm import tqdm

from analysis_duplication import load_graph
from analysis_intra import calculate_sample_size

FILE_INTRA = 'categories_intra_inter/samples_inter_labels.csv'
PREFIX = 'https://github.com/'
G = load_graph('dup_network.db')

df = pd.read_csv(FILE_INTRA)
print(df.head())

random.seed(123)

repos = list(df['repo'])
# remove  https://github.com/ from the beginning of the repos
repos = [r[19:] for r in repos]
# print(repos[0:10])

def get_population(G):
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
    return population

def sample_inter(G, sample):
    ccs = [[n for n in sorted(c, key=lambda x: G.nodes[x]['first_commit'])] for c in
           list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    first_commit_metamodels = [c[0] for c in ccs]

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
    return df


population = get_population(G)

# remove those repos that are not in the population
df = df[df['repo'].isin([PREFIX + s for s in population])].reset_index()

df_new = sample_inter(G, [r[19:] for r in df['repo']])

review_again = [False] * len(df)
df['metamodels_fix'] = df_new['metamodels']
df['originals_fix'] = df_new['originals']
df['originals_links_fix'] = df_new['originals_links']

# for loop the rows of df_new and df
for index, row in df_new.iterrows():
    repo = row['repo']
    assert repo == df.at[index, 'repo']
    metamodels = row['metamodels']
    original = row['originals']
    original_link = row['originals_links']

    if len(df.at[index, 'metamodels']) == len(metamodels) and \
            len(df.at[index, 'originals']) == len(original):
        continue
    else:
        review_again[index] = True
        print(repo)

df['review_again?'] = review_again
df.to_csv('samples_inter_fix.csv', index=False)

# sample new
population = [s for s in population if s not in [r[19:] for r in df['repo']]]

k = len(pd.read_csv(FILE_INTRA)) - len(df)
sample = random.sample(population, k)

df_compensation = sample_inter(G, sample)
df_compensation.to_csv('samples_inter_compensation.csv', index=False)

