import os

import pandas as pd
from git import Repo

from util import paths, helpers


def analyze_unsaved_dataset_files():
    dataset_files = pd.read_csv(paths.DATASET_FILES_FILE)
    repo_names = dataset_files['repository_name'].unique()

    ignored_files = []
    for repo_name in repo_names:
        repo = Repo(os.path.join(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY,
                                 helpers.get_dir_name_from_repo_name(repo_name)))

        repo_files = dataset_files[dataset_files['repository_name'] == repo_name]
        unsaved_files = repo_files[(repo_files['dataset_location'] == 'file system (not saved in VCS)') | (repo_files[
                                                                                                               'dataset_location'] == 'file system (not saved in VCS - outside of the repository)')]
        unsaved_file_paths = unsaved_files['dataset_path']
        for unsaved_file_path in unsaved_file_paths:
            ignored_paths = repo.ignored(unsaved_file_path)
            if len(ignored_paths) > 0:
                # print(repo_name, unsaved_file_path, ignored_paths)
                ignored_files.append([repo_name, ignored_paths[0]])

    return ignored_files


def analyze_unsaved_model_files():
    model_files = pd.read_csv(paths.MODEL_FILES_FILE)
    repo_names = model_files['repository_name'].unique()

    ignored_files = []
    for repo_name in repo_names:
        repo = Repo(os.path.join(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY,
                                 helpers.get_dir_name_from_repo_name(repo_name)))

        repo_files = model_files[model_files['repository_name'] == repo_name]
        unsaved_files = repo_files[(repo_files['model_location'] == 'file system (not saved in VCS)') | (repo_files[
                                                                                                             'model_location'] == 'file system (not saved in VCS - outside of the repository)')]
        unsaved_file_paths = unsaved_files['model_path']
        for unsaved_file in unsaved_files.itertuples():
            unsaved_file_path = unsaved_file.model_path
            ignored_paths = repo.ignored(unsaved_file_path)
            if len(ignored_paths) > 0:
                # print(repo_name, unsaved_file_path, ignored_paths)
                ignored_files.append([repo_name, ignored_paths[0], unsaved_file.is_self_pre_trained])

    return ignored_files


if __name__ == '__main__':
    ignored_dataset_files = analyze_unsaved_dataset_files()
    dataset_repo_names = [ignored_dataset_file[0] for ignored_dataset_file in ignored_dataset_files]
    print(f'{len(set(dataset_repo_names))} repositories has {len(ignored_dataset_files)} ignored dataset files')

    ignored_model_files = analyze_unsaved_model_files()
    model_repo_names = [ignored_model_file[0] for ignored_model_file in ignored_model_files]
    self_trained_model_files = [ignored_model_file[2] for ignored_model_file in ignored_model_files if ignored_model_file[2] == 'True']
    print(f'{len(set(model_repo_names))} repositories has {len(ignored_model_files)} ignored model files')
    print(f'Among the {len(ignored_model_files)} model files, {len(self_trained_model_files)} are self-trained')

    unique_repo_names = set(dataset_repo_names + model_repo_names)
    print(f'Total {len(unique_repo_names)} repositories has ignored dataset and model files')
