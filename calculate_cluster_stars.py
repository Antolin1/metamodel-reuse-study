from analysis_duplication import load_graph
import argparse
import networkx as nx
import csv

def main(args):
    G = load_graph(args.db)
    ccs = [c for c in list(sorted(nx.connected_components(G), key=len, reverse=True)) if len(c) > 1]
    with open('cluster_stars.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["cluster", "original", "original_path", "duplicate", "duplicate_path"])
        for cluster, cc in enumerate(ccs):
            sorted_nodes = list(sorted(cc, key=lambda x: G.nodes[x]['first_commit']))
            original_node = sorted_nodes[0]
            original_node_path = G.nodes[original_node]["local_path"]
            for n in sorted_nodes[1:]:
                writer.writerow([cluster, original_node, original_node_path, n, G.nodes[n]["local_path"]])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
