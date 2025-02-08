import csv
import os
import sqlite3
import time
from datetime import datetime

import pandas as pd
import requests
from github import Github, RateLimitExceededException, UnknownObjectException
from tqdm import tqdm

TOKEN = os.environ['GH_TOKEN']
FILE = 'listOfEcoreFiles.csv'
OUT_FOLDER = 'metamodels'
CONN = sqlite3.connect('dup_network.db')
CURSOR = CONN.cursor()

def download_data(output_filename, file_content):
    raw_url = file_content.download_url
    # print(raw_url)
    response = requests.get(raw_url)
    if response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        # print(f"File downloaded successfully as {output_filename}.")
        return True
    return False

def download_github_file(repo_name, file_path, output_filename, cutoff_date="2019-12-31"):
    g = Github(TOKEN)
    cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d")
    repo = None
    while True:
        try:
            if repo is None:
                repo = g.get_repo(repo_name)

            commits = repo.get_commits(until=cutoff_date)
            if commits.totalCount == 0:
                # print(f"No commits before the cutoff_data {cutoff_date}")
                return None

            for commit in commits:
                file_content = repo.get_contents(file_path, ref=commit.sha)
                # print(commit.sha)
                if download_data(output_filename, file_content):
                    return commit.commit.committer.date  # Exit loop if successful
                else:
                    # print(f"Failed to download {file_path} from {repo_name} at {commit.commit.committer.date}")
                    return None

        except RateLimitExceededException:
            # print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except UnknownObjectException:
            # print("Repo not found possibly")
            return None
        except:
            # print("Encoding problems probably")
            return None


def register_to_db(user, repo, path, local_path, date):
    tuple = (user,
             repo,
             path,
             local_path,
             date)
    CURSOR.execute("INSERT INTO metamodels (user, repo, "
                   "repo_path, local_path, considered_commit) VALUES (?, ?, ?, ?, ?)",
                   tuple)
    CONN.commit()

# registered metamodels
query_registerd = 'SELECT local_path from metamodels'
df_registered = pd.read_sql_query(query_registerd, CONN)
list_registered = set(list(df_registered['local_path']))

os.makedirs(OUT_FOLDER, exist_ok=True)
cont = 0
with open(FILE, mode='r', newline='') as file:
    reader = list(csv.reader(file))
    for row in tqdm(reader):
        p = row[0]
        if p in list_registered:
            continue
        user = p.split('$')[0]
        repo = p.split('$')[1]
        path = '/'.join(p.split('$')[-1].split("#"))

        # print(p)
        date = download_github_file(user + '/' + repo, path, os.path.join(OUT_FOLDER, p))
        time.sleep(1)
        if date:
            cont += 1
            register_to_db(user, repo, path, p, date)
        else:
            print(f"Failed to download {p}")

# print(f"Downloaded {cont} files")
CONN.close()
