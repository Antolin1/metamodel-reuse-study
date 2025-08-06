import argparse
import logging
import os
import random
import time
import csv
from datetime import datetime, timezone

from github import Github, GithubException

token = os.environ.get('GH_TOKEN')
if token is None:
    print("GH_TOKEN variable required")
    exit(-1)

GITHUB = Github(token, per_page=100)
LOGGER = logging.getLogger()
USERS_TO_IGNORE = ['modelset', 'mar-platform', 'models-lab', 'Antolin1', 'jesusc']


def load_existing_ids(csv_path):
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['id'] for row in reader}


def append_to_csv(csv_path, row, header):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def api_wait_search():
    limits = GITHUB.get_rate_limit()
    reset = limits.search.reset.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    seconds = (reset - now).total_seconds()
    LOGGER.info(f"Rate limit exceeded. Reset in {seconds:.3g} seconds.")
    if seconds > 0.0:
        time.sleep(seconds)
        LOGGER.info("Done waiting - resume!")


def process_file(f, already_processed_ids, csv_path):
    repo = f.repository
    model_id = f"{repo.full_name}/{f.path}"

    if repo.owner.login in USERS_TO_IGNORE:
        LOGGER.info(f"Skipping {model_id} (user: {repo.owner.login})")
        return

    if model_id in already_processed_ids:
        LOGGER.info(f"Already processed {model_id}")
        return

    try:
        # Last commit in the entire repository
        repo_last_commit = repo.get_commits()[0]

        # All commits that touched the file
        commits = list(repo.get_commits(path=f.path))
        if not commits:
            LOGGER.warning(f"No commits found for {model_id}")
            return

        file_last_commit = commits[0]
        file_first_commit = commits[-1]

        row = {
            'id': model_id,
            'path': f.path,
            'repo_name': repo.full_name,
            'user': repo.owner.login,
            'repo_last_commit_sha': repo_last_commit.sha,
            'repo_last_commit_date': repo_last_commit.commit.committer.date.isoformat(),
            'repo_creation_date': repo.created_at.isoformat(),
            'file_last_commit_sha': file_last_commit.sha,
            'file_last_commit_date': file_last_commit.commit.committer.date.isoformat(),
            'file_creation_date': file_first_commit.commit.committer.date.isoformat()
        }

        append_to_csv(csv_path, row, header=row.keys())
        already_processed_ids.add(model_id)

    except GithubException as e:
        LOGGER.warning(f"GitHubException for {model_id}: {e}")
        api_wait_search()


def search_github(csv_path, already_processed_ids, step=5, init=512, end=1_000_000, hint='EPackage', extension='ecore'):
    initial_step = step
    iterations_without_downloading = 0
    last_size = init
    total = 0

    for i in range(init, end, step):
        iterations_without_downloading += 1
        step = initial_step * iterations_without_downloading
        finished_chunk = False

        while not finished_chunk:
            try:
                size = f'size:{i}..{i + step - 1}'
                LOGGER.info(f"Querying {size}")
                files = GITHUB.search_code(query=f'{hint} extension:{extension} {size}')
                LOGGER.info(f"Found {files.totalCount} files")

                for f in files:
                    LOGGER.info(f"Processing {total}... {f.name}")
                    time.sleep(random.uniform(1, 2))
                    process_file(f, already_processed_ids, csv_path)
                    iterations_without_downloading = 0
                    last_size = f.size
                    total += 1

                finished_chunk = True

            except GithubException:
                api_wait_search()
                if i == last_size:
                    i += 1
                else:
                    i = last_size
                LOGGER.info(f"Retrying from size: {last_size}")


def main(args):
    already_processed_ids = load_existing_ids(args.output_csv)
    search_github(
        csv_path=args.output_csv,
        already_processed_ids=already_processed_ids,
        step=args.step,
        init=args.init,
        end=args.end
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl GitHub for Ecore file metadata')
    parser.add_argument('--output_csv', default='ecore_metadata.csv')
    parser.add_argument('--step', default=5, type=int)
    parser.add_argument('--init', default=512, type=int)
    parser.add_argument('--end', default=30_000_000, type=int)
    parser.add_argument('--logger', default='ecore_github_crawler.log')
    args = parser.parse_args()

    LOGGER.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    LOGGER.addHandler(console)

    file_handler = logging.FileHandler(args.logger)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s | %(filename)s:%(lineno)d] - %(levelname)s: %(message)s'))
    LOGGER.addHandler(file_handler)

    main(args)

