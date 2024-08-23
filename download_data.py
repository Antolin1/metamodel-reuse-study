import csv
import os
import sqlite3
import time

from github import Github, RateLimitExceededException, UnknownObjectException
from tqdm import tqdm

TOKEN = os.environ['GH_TOKEN']
FILE = 'listOfEcoreFiles.csv'
OUT_FOLDER = 'metamodels'
CONN = sqlite3.connect('dup_network.db')
CURSOR = CONN.cursor()


def get_metadata(repo, file_path):
    commits = [c for c in repo.get_commits(path=file_path)]

    # Get the first (oldest) commit
    first_commit = commits[-1]
    first_commit_author = first_commit.commit.committer.name
    first_commit_date = first_commit.commit.committer.date

    # Get the last (most recent) commit
    last_commit = commits[0]
    last_commit_date = last_commit.commit.committer.date
    return {"author": first_commit_author, "first_commit": first_commit_date, "last_commit": last_commit_date}


def download_github_file(repo_name, file_path, output_filename):
    g = Github(TOKEN)
    repo = None
    while True:
        try:
            if repo is None:
                repo = g.get_repo(repo_name)
            file_content = repo.get_contents(file_path)
            raw_data = file_content.decoded_content

            with open(output_filename, "wb") as file:
                file.write(raw_data)
            print(f"File downloaded successfully as {output_filename}.")
            metadata = get_metadata(repo, file_path)
            return metadata  # Exit loop if successful

        except RateLimitExceededException:
            print("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except UnknownObjectException:
            print("Repo not found possibly")
            return None
        except:
            print("Encoding problems probably")
            return None


def register_to_db(user, repo, path, local_path, metadata):
    tuple = (user,
             repo,
             path,
             local_path,
             metadata["first_commit"].strftime('%Y-%m-%d %H:%M:%S'),
             metadata["last_commit"].strftime('%Y-%m-%d %H:%M:%S'),
             metadata["author"])
    CURSOR.execute("INSERT INTO metamodels (user, repo, "
                   "repo_path, local_path, first_commit, last_commit, author) VALUES (?, ?, ?, ?, ?, ?, ?)",
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

        print(user, repo, path)
        print(p)
        metadata = download_github_file(user + '/' + repo, path, os.path.join(OUT_FOLDER, p))
        if metadata:
            cont += 1
            register_to_db(user, repo, path, p, metadata)

        # https://raw.githubusercontent.com/kit-sdq-emf-refactor-fork/edu.kit.ipd.sdq.emf.refactor/master/edu.kit.ipd.sdq.emf.refactor.tests/HubLike_Incoming.ecore

print(f"Downloaded {cont} files")
CONN.close()
