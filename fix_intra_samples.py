import json
import random

import networkx as nx
import pandas as pd
from tqdm import tqdm

from analysis_duplication import load_graph
from analysis_intra import calculate_sample_size

FILE_INTRA = 'categories_intra_inter/samples_intra_labels.csv'

G = load_graph('dup_network.db')

df = pd.read_csv(FILE_INTRA)
print(df.head())

repos = list(df['repo'])

def intra_project_reuse(G, repos):
    # repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    result = {}
    files = {}
    for repo in tqdm(repos, total=len(repos)):
        view = nx.subgraph_view(G, filter_node=lambda n: G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] == repo)
        ccs = [c for c in list(sorted(nx.connected_components(view), key=len, reverse=True))]
        score = sum([len(c) - 1 for c in ccs])
        result[repo] = score
        files[repo] = [[G.nodes[n]['local_path'] for n in c] for c in ccs if len(c) > 1]



    sample_files = [json.dumps(files[s]) for s in repos]

    df['fixed'] = sample_files
    review_again = [False] * len(repos)

    # iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        fixed_version = json.loads(row['fixed'])
        try:
            previous = json.loads(row['files'])
        except:
            print(row['repo'])
            review_again[index] = True
            continue

        fixed_version = frozenset([frozenset(c) for c in fixed_version])
        previous = frozenset([frozenset(c) for c in previous])

        # check if the previous version is in the fixed version
        if previous != fixed_version:
            print(row['repo'])
            # print prevoius that is not in fixed
            print(fixed_version - previous)
            review_again[index] = True
        else:
            # set df fixed empy
            df.at[index, 'fixed'] = ""

    df['review_again?'] = review_again
    df.to_csv('samples_intra_fix.csv', index=False)

intra_project_reuse(G, repos)

print(calculate_sample_size(832, 1.96, 0.5, 0.05))
print(calculate_sample_size(828, 1.96, 0.5, 0.05))
