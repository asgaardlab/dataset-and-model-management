import os

import git
import pandas as pd

from util import paths, helpers

repo_count = 1


def get_commit_hashes_for_file(repo, file_path):
    commit_hashes = []
    for commit in repo.iter_commits(paths=file_path):
        commit_hashes.append(commit.hexsha)
    return commit_hashes


def get_commits_for_renamed_file(repo, file_path):
    commits = []
    for commit in repo.iter_commits():
        # Get the tree for the commit
        tree = commit.tree

        # Check if the file_path exists in the tree
        if file_path in tree:
            commits.append(commit)
        else:
            # Check if the file_path was renamed in this commit
            for diff in commit.diff(commit.parents[0]):
                if diff.b_path == file_path:
                    commits.append(commit)
                    break
    return commits


def list_commits_of_file(repo, file_path, location_of):
    commit_hashes = get_commit_hashes_for_file(repo, file_path)
    renamed_commits = []  # get_commits_for_renamed_file(repo, file_path)

    print(f'Total {len(commit_hashes)} + {len(renamed_commits)} commits for {file_path} {location_of} file')

    return commit_hashes + renamed_commits


def list_file_changing_commits_in_repo(repo_file_paths, save_file_path, repo_name, file_type, total):
    global repo_count
    print(f'[{repo_count}/{total}] {repo_name} ({len(repo_file_paths)})')
    repo_path = os.path.join(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY,
                             helpers.get_dir_name_from_repo_name(repo_name))
    repo = git.Repo(repo_path)

    repo_file_changing_commits = []
    for file_path in repo_file_paths:
        file_changing_commit_hashes = list_commits_of_file(repo, file_path, file_type)
        repo_file_changing_commits.append([repo_name, file_type, file_path, len(file_changing_commit_hashes),
                                           file_changing_commit_hashes])
    repo_count += 1

    repo_dataset_commits_df = pd.DataFrame(repo_file_changing_commits)
    repo_dataset_commits_df.to_csv(save_file_path, mode='a', index=False, header=False)


def list_file_changing_commits():
    save_path = os.path.join(paths.DATA_DIRECTORY, 'file_path_with_#_of_commits.csv')
    if os.path.exists(save_path):
        os.remove(save_path)

        empty_df = pd.DataFrame(
            columns=['repo_name', 'location_of', 'location', '#_of_commits', 'file_changing_commit_hashes'])
        empty_df.to_csv(save_path, mode='a', index=False)

    dataset_files = pd.read_csv(paths.DATASET_FILES_FILE)
    dataset_files_in_vcs = dataset_files[dataset_files['dataset_location'] == 'file system (saved in VCS)']

    repos = dataset_files_in_vcs.groupby('repository_name')
    repos.apply(lambda repo: list_file_changing_commits_in_repo(repo['dataset_path'], save_path, repo.name, 'dataset',
                                                                len(repos)))

    model_files = pd.read_csv(paths.MODEL_FILES_FILE)
    model_files_in_vcs = model_files[model_files['model_location'] == 'file system (saved in VCS)']

    repos = model_files_in_vcs.groupby('repository_name')
    global repo_count
    repo_count = 1
    repos.apply(
        lambda repo: list_file_changing_commits_in_repo(repo['model_path'], save_path, repo.name, 'model', len(repos)))


if __name__ == '__main__':
    list_file_changing_commits()
