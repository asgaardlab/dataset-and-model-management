import time
from itertools import cycle
from urllib.parse import urlparse, parse_qs

import requests
from github import Github, RateLimitExceededException
from github.GithubException import GithubException

from util.helpers import print_error

tokens = []  # tokens are in github_tokens.csv file

PAGE_SIZE = 100
g_list = cycle(Github(t, per_page=PAGE_SIZE) for t in tokens)
token_cycle = cycle(t for t in tokens)


def g():
    return next(g_list)


def has_file_in_repo(full_name, filename):
    try:
        results = g().search_code(query=f'filename:{filename} repo:{full_name}')
        if results.totalCount:
            return True, results
        else:
            return False, results
    except RateLimitExceededException:
        time.sleep(60)
        return has_file_in_repo(full_name, filename)
    except (GithubException, Exception) as e:
        print_error(e)
        return False, []


def get_commits_count(repo_full_name: str, index: int) -> int:
    url = f'https://api.github.com/repos/{repo_full_name}/commits?per_page=1'
    token = next(token_cycle)
    headers = {"Authorization": f"Bearer {token}"}

    time.sleep(1)
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        links = r.links
        rel_last_link_url = urlparse(links["last"]["url"])
        rel_last_link_url_args = parse_qs(rel_last_link_url.query)
        rel_last_link_url_page_arg = rel_last_link_url_args["page"][0]
        commits_count = int(rel_last_link_url_page_arg)
    else:
        commits_count = 0
    print(f'[{index + 1} ({token})] {commits_count} commits in {repo_full_name}')
    return commits_count
