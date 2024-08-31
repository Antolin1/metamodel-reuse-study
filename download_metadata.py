import os
import sqlite3
import time

import pandas as pd
from github import RateLimitExceededException, UnknownObjectException, Github
from tqdm import tqdm

TOKEN = os.environ['GH_TOKEN']
CONN = sqlite3.connect('dup_network.db')
CURSOR = CONN.cursor()


def get_metadata(repo, file_path):
    commits = [c for c in repo.get_commits(path=file_path)]

    # Get the first (oldest) commit
    first_commit = commits[-1]
    first_commit_author = first_commit.commit.committer.name
    first_commit_date = first_commit.commit.committer.date

    return {"author": first_commit_author, "first_commit": first_commit_date}


def access_pygithub(user, repo_name, repo_path):
    repo = None
    g = Github(TOKEN)
    while True:
        try:
            if repo is None:
                repo = g.get_repo(user + '/' + repo_name)

            metadata = get_metadata(repo, repo_path)
            return metadata

        except RateLimitExceededException:
            print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except UnknownObjectException:
            print("Repo not found possibly")
            return None
        except:
            print("Encoding problems probably")
            return None


conn = sqlite3.connect('dup_network.db')
query = f'SELECT id, user, repo, repo_path FROM metamodels WHERE author IS NULL OR first_commit IS NULL'
df = pd.read_sql_query(query, conn)

for index, row in tqdm(df.iterrows(), total=len(df)):
    metadata = access_pygithub(row['user'], row['repo'], row['repo_path'])
    if metadata:
        CURSOR.execute("UPDATE metamodels SET first_commit=?, author=? WHERE id=?", (metadata["first_commit"],
                                                                                     metadata["author"],
                                                                                     row['id']))
        CONN.commit()

CONN.close()
