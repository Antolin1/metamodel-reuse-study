import argparse
from collections import defaultdict

from analysis_duplication import load_graph


def main(args):
    G = load_graph(args.db)

    total_metamodels = len(G)
    print(f"Number of total meta-models: {total_metamodels}")
    repos = set([G.nodes[n]['user'] + '/' + G.nodes[n]['repo'] for n in G])
    total_repositories = len(repos)
    print(f"Number of total repositories: {total_repositories}")

    # top 10 users with the largest number of repositories
    users = defaultdict(int)
    for r in repos:
        user = r.split('/')[0]
        users[user] += 1

    print("Top 10 users with the largest number of repositories")
    for user in sorted(users, key=users.get, reverse=True)[:10]:
        print(f"{user} {users[user]}")

    print(f"Number of users: {len(users)}")

    print(f"Mean repositories per user: {total_repositories / len(users):.2f}")
    print(f"Mean meta-models per repository: {total_metamodels / total_repositories:.2f}")

    # top 3 repositories with the largest number of meta-models
    repositories = defaultdict(int)
    for n in G:
        repositories[G.nodes[n]['user'] + '/' + G.nodes[n]['repo']] += 1

    print("Top 3 repositories with the largest number of meta-models")
    for repo in sorted(repositories, key=repositories.get, reverse=True)[:3]:
        print(f"{repo} {repositories[repo]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='dup_network.db')
    args = parser.parse_args()
    main(args)
