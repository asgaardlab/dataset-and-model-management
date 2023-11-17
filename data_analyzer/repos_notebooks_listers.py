import glob
import os

import pandas as pd

from util import paths, helpers


def get_notebooks_of_repository(repo_dir_path):
    return glob.glob(repo_dir_path + '/**/*.ipynb', recursive=True)


def save_notebooks_path_of_repository(repo, repo_notebooks):
    notebooks = []
    for repo_notebook in repo_notebooks:
        notebooks.append([repo, helpers.get_relative_path_from_file_path(repo_notebook)])

    df = pd.DataFrame(notebooks)
    root = paths.MANUAL_ANALYSIS_DIRECTORY
    repo_dir_name = helpers.get_dir_name_from_repo_name(repo)
    file_name = 'notebooks.csv'
    save_dir = os.path.join(root, repo_dir_name)
    if not os.path.isdir(save_dir):
        save_dir = os.path.join(root, '_' + repo_dir_name)
    df.to_csv(os.path.join(save_dir, file_name), header=['repo_name', 'notebook_path'], index=False)


def list_repos_notebooks():
    repos = pd.read_csv(os.path.join(paths.DATA_DIRECTORY, 'min_100_committed_repositories_for_manual_analysis.csv'))['full_name'].values

    for repo in repos:
        repo_directory_path = os.path.join(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY, helpers.get_dir_name_from_repo_name(repo))
        repo_notebooks = get_notebooks_of_repository(repo_directory_path)
        if len(repo_notebooks) > 0:
            save_notebooks_path_of_repository(repo, repo_notebooks)


if __name__ == '__main__':
    list_repos_notebooks()
