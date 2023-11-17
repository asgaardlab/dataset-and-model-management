import collections
import os
import statistics
from pprint import pprint

import pandas as pd

from result_analyzer.common_plots import plot_groups_and_save, plot_file_sizes_per_location_group, plot_one_violin
from util import paths


def plot_dataset_location_groups(dataset_location_counts, save_file_path):
    data = [
        ['Database', dataset_location_counts['database (not saved in VCS)']],
        ['File System', dataset_location_counts['file system (not saved in VCS)']],
        ['Library', dataset_location_counts['library dataset']],
        ['Remote Storage', dataset_location_counts['online']],
        ['Repository', dataset_location_counts['file system (saved in VCS)']],
        ['Runtime Memory', dataset_location_counts['runtime memory']],
        ['Unknown Source', dataset_location_counts['unknown']]
    ]
    plot_data = pd.DataFrame(data, columns=['label', 'data'])

    plot_groups_and_save(plot_data, '# of data files from all repositories', 'Dataset storage locations', save_file_path)


def plot_dataset_sizes_per_location_group(dataset_files, save_file_path):
    files_with_valid_size = dataset_files[(dataset_files['dataset_size'] != '') &
                                          (dataset_files['dataset_size'] != 'unknown')]
    files_with_valid_size['dataset_size'] = files_with_valid_size['dataset_size'].apply(
        lambda size: float(size.split(' ')[0]))

    remote_file_sizes = files_with_valid_size[files_with_valid_size['dataset_location'] == 'online'][
        'dataset_size'].values.tolist()
    print(f'Median remote file size among {len(remote_file_sizes)} files: {statistics.median(remote_file_sizes)}')

    repository_file_sizes = \
        files_with_valid_size[files_with_valid_size['dataset_location'] == 'file system (saved in VCS)'][
            'dataset_size'].values.tolist()
    print(
        f'Median repository file size among {len(repository_file_sizes)} files: {statistics.median(repository_file_sizes)}')

    data = [
        ['Remote Storage', remote_file_sizes],
        ['Repository', repository_file_sizes]
    ]
    plot_data = pd.DataFrame(data, columns=['label', 'data'])
    plot_data = plot_data.explode('data')
    plot_data['data'] = plot_data['data'].astype('float')

    plot_file_sizes_per_location_group(plot_data, max(repository_file_sizes), 'Size of data files (in MB)',
                                       'Dataset storage locations', save_file_path)


def plot_file_distribution_per_repo(files, save_file_path):
    files_per_repo_count = files.groupby('repository_name').size().values.tolist()
    files_per_repo_count += ([0] * (93 - files['repository_name'].nunique()))

    print(f'Median repo has {statistics.median(files_per_repo_count)} data files')

    plot_one_violin(files_per_repo_count, '# of data files per repository', save_file_path)


def file_storage_distribution_per_repo(files, file_save_file_path):
    files_per_repo_count = files.groupby('repository_name').size().to_frame('#_of_files_in_repo')
    repo_names_having_more_than_one_file = files_per_repo_count[files_per_repo_count['#_of_files_in_repo'] > 1].index
    print(f'{len(repo_names_having_more_than_one_file)} repos have more than 1 data file')

    repos_having_more_than_one_file = files[files['repository_name'].isin(repo_names_having_more_than_one_file)]

    locations_per_repo = repos_having_more_than_one_file.groupby(['repository_name'])[
        'dataset_location'].unique().to_frame('dataset_locations').reset_index()
    locations_per_repo['#_of_dataset_locations'] = locations_per_repo['dataset_locations'].apply(lambda l: len(l))
    print(
        f'Among them, {len(locations_per_repo[locations_per_repo["#_of_dataset_locations"] == 1])} repos use single storage to store all data files')

    locations_per_repo.to_csv(file_save_file_path, index=False)


def plot_per_storage_per_repo_files(files, save_file_path):
    storages_per_repo = files.groupby('repository_name')['dataset_location'].unique().to_frame('dataset_locations')
    storages = storages_per_repo['dataset_locations'].explode().tolist()
    storage_dict = dict(collections.Counter(storages))

    data = [
        ['Database', storage_dict['database (not saved in VCS)']],
        ['File System', storage_dict['file system (not saved in VCS)']],
        ['Library', storage_dict['library dataset']],
        ['Remote Storage', storage_dict['online']],
        ['Repository', storage_dict['file system (saved in VCS)']],
        ['Runtime Memory', storage_dict['runtime memory']],
        ['Unknown Source', storage_dict['unknown']]
    ]

    plot_data = pd.DataFrame(data, columns=['label', 'data'])

    plot_groups_and_save(plot_data, '# of repositories using the storage', 'Dataset storage locations', save_file_path,
                         show_percentage=False)


if __name__ == '__main__':
    dataset_files = pd.read_csv(paths.DATASET_FILES_FILE, dtype={'dataset_size': str}, na_filter=False)
    pprint(dict(collections.Counter(dataset_files['dataset_location'].values.tolist())))

    dataset_files['dataset_location'].replace('file system (not saved in VCS - outside of the repository)',
                                              'file system (not saved in VCS)', regex=False, inplace=True)
    dataset_files['dataset_location'].replace('untraceable', 'unknown', regex=False, inplace=True)

    graph_save_root = os.path.join(paths.DATA_DIRECTORY, 'graphs', 'plots_on_dataset')

    graph_save_file_path = os.path.join(graph_save_root, 'dataset_file_distribution_per_repo.pdf')
    plot_file_distribution_per_repo(dataset_files, graph_save_file_path)

    file_save_file_path = os.path.join(paths.DATA_DIRECTORY, 'dataset_storage_locations_per_repo.csv')
    file_storage_distribution_per_repo(dataset_files, file_save_file_path)

    graph_save_file_path = os.path.join(graph_save_root, 'per_storage_per_repo_data_files.pdf')
    plot_per_storage_per_repo_files(dataset_files, graph_save_file_path)

    dataset_location_groups = dict(collections.Counter(dataset_files['dataset_location'].values.tolist()))
    pprint(dataset_location_groups)

    graph_save_file_path = os.path.join(graph_save_root, 'dataset_location_groups.pdf')
    plot_dataset_location_groups(dataset_location_groups, graph_save_file_path)

    graph_save_file_path = os.path.join(graph_save_root, 'dataset_sizes_per_location.pdf')
    plot_dataset_sizes_per_location_group(dataset_files, graph_save_file_path)
