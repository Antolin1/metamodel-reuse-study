import csv
import os
import sqlite3
import time
from datetime import datetime

from github import Github, RateLimitExceededException, UnknownObjectException
from tqdm import tqdm

TOKEN = os.environ['GH_TOKEN']
FILE = 'listOfEcoreFiles.csv'
OUT_FOLDER = 'metamodels'
CONN = sqlite3.connect('dup_network.db')
CURSOR = CONN.cursor()


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
                print(f"No commits before the cutoff_data {cutoff_date}")
                return None

            for commit in commits:
                file_content = repo.get_contents(file_path, ref=commit.sha)
                raw_data = file_content.decoded_content
                with open(output_filename, "wb") as file:
                    file.write(raw_data)
                print(f"File downloaded successfully as {output_filename}.")
                return commit.commit.committer.date  # Exit loop if successful

        except RateLimitExceededException:
            print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except UnknownObjectException:
            print("Repo not found possibly")
            return None
        except:
            print("Encoding problems probably")
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


os.makedirs(OUT_FOLDER, exist_ok=True)
cont = 0
with open(FILE, mode='r', newline='') as file:
    reader = list(csv.reader(file))
    for row in tqdm(reader):
        p = row[0]
        user = p.split('$')[0]
        repo = p.split('$')[1]
        path = '/'.join(p.split('$')[-1].split("#"))

        print(p)
        date = download_github_file(user + '/' + repo, path, os.path.join(OUT_FOLDER, p))
        time.sleep(1)
        if date:
            cont += 1
            register_to_db(user, repo, path, p, date)

print(f"Downloaded {cont} files")
CONN.close()
