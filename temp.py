from github import Github
import requests
from datetime import datetime

# Authenticate with GitHub
g = Github("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")


def download_file_before_date(owner, repo_name, file_path, cutoff_date):
    # Get the repository
    repo = g.get_repo(f"{owner}/{repo_name}")

    # Convert cutoff_date to a datetime object
    cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d")

    # Find the last commit before the cutoff date
    for commit in repo.get_commits(until=cutoff_date):
        file_content = repo.get_contents(file_path, ref=commit.sha)
        raw_data = file_content.decoded_content
        print(raw_data)
        return


# Example usage
owner = "eclipse"
repo_name = "epsilon"
file_path = "pom.xml"
cutoff_date = "2019-12-31"

download_file_before_date(owner, repo_name, file_path, cutoff_date)
