import os
import shutil
import time
from urllib import request

import github
import pandas as pd

from util import paths, helpers
from util.github_api_client import has_file_in_repo
from util.helpers import print_error


def get_download_directory(root_directory, full_name):
    return os.path.join(root_directory, helpers.get_dir_name_from_repo_name(full_name))


def save_file(response, repository_directory, search_result):
    saved_path = os.path.join(repository_directory, search_result.path.replace('/', '@'))
    with open(os.path.abspath(saved_path), 'w') as file:
        file.write(response.text)
    return saved_path


def download_files(search_results, download_directory):
    saved_paths = list()
    try:
        for search_result in search_results:
            relative_file_path = search_result.path.replace('/', '@')
            save_path = os.path.join(download_directory, relative_file_path)
            try:
                request.urlretrieve(search_result.download_url, save_path)
                saved_paths.append(relative_file_path)
            except Exception as e:
                print_error(e)
        return saved_paths
    except github.RateLimitExceededException:
        time.sleep(1)
        return download_files(search_results, download_directory)


def search_and_download_requirements_file(repository_full_name, root_download_dir, index, total):
    print(f'[{index + 1}|{total}] downloading requirements file for {repository_full_name}')

    download_dir = get_download_directory(root_download_dir, repository_full_name)
    if os.path.exists(download_dir):
        return

    has_requirements_file, results = has_file_in_repo(repository_full_name, 'requirements.txt')

    if has_requirements_file:
        helpers.create_directory_if_not_exists(download_dir)
        download_files(results, download_dir)


def has_requirements_files(repo_name):
    repo_directory = os.path.join(paths.REQUIREMENTS_FILES_DIRECTORY, helpers.get_dir_name_from_repo_name(repo_name))

    if os.path.isdir(repo_directory):
        req_file_paths = [req_file.name for req_file in os.scandir(repo_directory)]

        if len(req_file_paths) == 0:
            print(f'{repo_directory} is empty')
            shutil.rmtree(repo_directory)
            return False

        return True
    return False


def save_result(repositories):
    if 'has_requirements_files' in repositories:
        repositories = repositories.drop('has_requirements_files', axis=1)
    repositories['has_requirements_files'] = repositories.apply(lambda repo: has_requirements_files(repo['full_name']), axis=1)
    repositories.to_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE, index=False)


def download_requirements_files():
    repositories = pd.read_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE)

    os.makedirs(paths.REQUIREMENTS_FILES_DIRECTORY, exist_ok=True)

    repositories.apply(lambda repo: search_and_download_requirements_file(repo['full_name'],
                                                                          paths.REQUIREMENTS_FILES_DIRECTORY,
                                                                          repo.name, len(repositories)),
                       axis=1)
    save_result(repositories)


if __name__ == "__main__":
    download_requirements_files()
