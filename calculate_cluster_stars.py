from tqdm import tqdm
from analysis_duplication import load_graph
import argparse
import networkx as nx
import csv
import pandas as pd


def calculate_inter_stars(G):
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    filename = "cluster_stars.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["cluster", "original", "original_path", "duplicate", "duplicate_path"])
        for cluster, cc in enumerate(ccs):
            sorted_nodes = list(sorted(cc, key=lambda x: G.nodes[x]['first_commit']))
            original_node = sorted_nodes[0]
            original_node_path = G.nodes[original_node]["local_path"]

            # Could be improved by avoiding nodes in the same repo than the original
            # This filtering is done below
            for n in sorted_nodes[1:]:
                writer.writerow([cluster, original_node, original_node_path, n, G.nodes[n]["local_path"]])

    # filter out the file to only include inter duplications
    df = pd.read_csv(filename)
    df['repo_original'] = df['original_path'].str.split('$').str[0] + '/' + df['original_path'].str.split('$').str[1]
    df['repo_duplicate'] = df['duplicate_path'].str.split('$').str[0] + '/' + df['duplicate_path'].str.split('$').str[1]
    df['inter'] = df['repo_original'] != df['repo_duplicate']

    data_inter = df[df["inter"]].copy()
    data_inter.drop(columns=["inter", "repo_original", "repo_duplicate"], inplace=True)
    data_inter.to_csv('cluster_stars-inter.csv', index=False)

def calculate_intra_stars(G):
    node_to_repo = {n : G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G} # to speedup filter
    repos = set(node_to_repo[n] for n in G)

    count = 0
    with open('cluster_stars-intra.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["repo", "repo_name", "cluster", "original", "original_path", "duplicate", "duplicate_path"])

        for repo in tqdm(repos, total=len(repos)):
            view = nx.subgraph_view(G, filter_node=lambda n: node_to_repo[n] == repo)
            ccs = [c for c in list(nx.connected_components(view))]
            intra_dups = sum([len(c) - 1 for c in ccs])

            if intra_dups > 0:
                count += 1
                cluster = 0

                for cc in ccs:
                    # if it's an intra-duplication, process the repo cluster
                    if (len(cc) > 1):
                        sorted_nodes = list(sorted(cc, key=lambda x: G.nodes[x]['first_commit']))
                        original_node = sorted_nodes[0]
                        original_node_path = G.nodes[original_node]["local_path"]
                        for n in sorted_nodes[1:]:
                            writer.writerow([count, repo, cluster, original_node, original_node_path, n, G.nodes[n]["local_path"]])
                        cluster += 1

    print(f"Repos with intra-duplications: {count}")

def main(args):
    G = load_graph(args.db)

    calculate_inter_stars(G)
    calculate_intra_stars(G)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
