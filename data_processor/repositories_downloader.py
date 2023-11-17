import os

import git
import pandas as pd
from git import GitCommandError
from git import Repo

from util import helpers, paths

error_count = 0


class Progress(git.remote.RemoteProgress):
    def update(self, *args):
        print(self._cur_line)


def repository_exists(repository_directory_name: str):
    directory = os.path.abspath(repository_directory_name)
    return os.path.isdir(directory)


def handle_git_exception(repository_full_name: str, event: str, exception: Exception):
    global error_count
    error_count += 1
    print(f'\033[91m[{error_count}] Error in {event} {repository_full_name}: {exception}\033[0m')


def pull(repository_full_name: str, repository_directory_name: str, index: int, total: int):
    print(f'{index + 1}|{total} pulling {repository_full_name} to {repository_directory_name}')
    try:
        repository = Repo(repository_directory_name)
        for remote in repository.remotes:
            remote.fetch()
    except GitCommandError as e:
        handle_git_exception(repository_full_name, 'pulling', e)


def clone(repository_full_name: str, clone_url: str, repository_directory_name: str, index: int, total: int):
    print(f'{index + 1}|{total} cloning {repository_full_name} from {clone_url} to {repository_directory_name}')
    try:
        Repo.clone_from(clone_url, repository_directory_name, progress=Progress(), depth=1)
    except GitCommandError as e:
        handle_git_exception(repository_full_name, 'cloning', e)


def get_repository(repository_full_name: str, clone_url: str, root_directory: str, index: int, total: int):
    repo_dir_path = os.path.join(root_directory, helpers.get_dir_name_from_repo_name(repository_full_name))

    if repository_exists(repo_dir_path):
        pull(repository_full_name, repo_dir_path, index, total)
    else:
        to_directory = repo_dir_path[:199] if len(repo_dir_path) > 200 else repo_dir_path
        clone(repository_full_name, clone_url, to_directory, index, total)

        if repository_exists(to_directory) and len(to_directory) != len(repo_dir_path):
            os.rename(to_directory, repo_dir_path)


def get_last_commit_hash(repository_full_name: str, root_directory: str):
    to_directory = os.path.join(root_directory, helpers.get_dir_name_from_repo_name(repository_full_name))

    if repository_exists(to_directory):
        repo = Repo(to_directory)
        return repo.head.object.hexsha

    return None


def download_repositories(repositories, download_directory, save_file_path):
    print(f'Downloading {len(repositories)} repositories...')
    os.makedirs(download_directory, exist_ok=True)
    repositories.apply(
        lambda repo: get_repository(repo['full_name'], repo['clone_url'], download_directory, repo.name,
                                    len(repositories)), axis=1)
    repositories['last_commit_hash'] = repositories.apply(
        lambda repo: get_last_commit_hash(repo['full_name'], download_directory), axis=1)

    repositories.to_csv(save_file_path, index=False)


if __name__ == '__main__':
    repos = pd.read_csv(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE)
    download_repositories(repos, paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY,
                          paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE)
