import os
import sqlite3
import time

import pandas as pd
import requests
from github import Github, RateLimitExceededException, UnknownObjectException
from tqdm import tqdm

TOKEN = os.environ['GH_TOKEN']
FILE = 'ecore_metadata.csv'
OUT_FOLDER = 'metamodels-new'
CONN = sqlite3.connect('dup_network_new.db')
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

def download_github_file(repo_name, file_path, output_filename, commit_sha):
    g = Github(TOKEN)
    repo = None
    while True:
        try:
            if repo is None:
                repo = g.get_repo(repo_name)

            file_content = repo.get_contents(file_path, ref=commit_sha)
            # print(commit.sha)
            return download_data(output_filename, file_content)
        except RateLimitExceededException:
            # print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except UnknownObjectException:
            # print("Repo not found possibly")
            return False
        except:
            # print("Encoding problems probably")
            return False




def register_to_db(user, repo, path, local_path, considered_commit, first_commit, repo_creation_date):
    tuple = (user,
             repo,
             path,
             local_path,
             considered_commit,
             first_commit,
             repo_creation_date)
    CURSOR.execute("INSERT INTO metamodels (user, repo, "
                   "repo_path, local_path, considered_commit, "
                   "first_commit, repo_creation_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   tuple)
    CONN.commit()

# registered metamodels
query_registerd = 'SELECT local_path from metamodels'
df_registered = pd.read_sql_query(query_registerd, CONN)
list_registered = set(list(df_registered['local_path']))

os.makedirs(OUT_FOLDER, exist_ok=True)

list_files = pd.read_csv(FILE)


cont = 0
for _, row in tqdm(list_files.iterrows(), total=len(list_files)):
    full_repo_name = row["repo_name"]
    user = full_repo_name.split('/')[0]
    repo = full_repo_name.split('/')[1]
    file_name = f"{user}${repo}${row['path'].replace('/', '#')}"
    if file_name in list_registered:
        continue
    was_downloaded = download_github_file(full_repo_name, row['path'], os.path.join(OUT_FOLDER, file_name), row['repo_last_commit_sha'])
    if was_downloaded:
        register_to_db(user, repo, row['path'], file_name, row['repo_last_commit_date'], row['file_creation_date'], row['repo_creation_date'])
        cont += 1
    else:
        print(f"Failed to download {file_name}")

# print(f"Downloaded {cont} files")
CONN.close()
