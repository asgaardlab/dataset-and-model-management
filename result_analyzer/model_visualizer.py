import collections
import os
import statistics
from pprint import pprint

import pandas as pd

from result_analyzer.common_plots import plot_groups_and_save, plot_file_sizes_per_location_group, \
    plot_multi_bar_and_save, plot_one_violin
from util import paths


def get_models_per_category(model_files):
    self_pre_trained_model_files = model_files[model_files['is_self_pre_trained'] == 'True']
    third_party_model_files = model_files[model_files['is_self_pre_trained'] == 'False']
    unknown_trainer_model_files = model_files[~model_files['is_self_pre_trained'].isin(['True', 'False'])]

    return self_pre_trained_model_files, third_party_model_files, unknown_trainer_model_files


def group_by_model_location(model_files):
    model_locations = model_files['model_location'].values.tolist()
    return dict(collections.Counter(model_locations))


def plot_model_location_groups(model_files, save_root):
    self_trained_model_files, pre_trained_model_files, unknown_trainer_model_files = get_models_per_category(
        model_files)

    self_trained_model_location_groups = group_by_model_location(self_trained_model_files)
    pprint(self_trained_model_location_groups)
    pre_trained_model_location_groups = group_by_model_location(pre_trained_model_files)
    pprint(pre_trained_model_location_groups)
    unknown_trainer_model_location_groups = group_by_model_location(unknown_trainer_model_files)
    pprint(unknown_trainer_model_location_groups)

    runtime_self_trained_models = self_trained_model_location_groups['runtime memory'] \
        if 'runtime memory' in self_trained_model_location_groups.keys() else 0
    runtime_pre_trained_models = pre_trained_model_location_groups['runtime memory'] \
        if 'runtime memory' in pre_trained_model_location_groups.keys() else 0

    data = [
        ['Self-trained model', 'File System', self_trained_model_location_groups['file system (not saved in VCS)']],
        ['Pre-trained model', 'File System', pre_trained_model_location_groups['file system (not saved in VCS)']],
        ['Self-trained model', 'Remote Storage', self_trained_model_location_groups['online']],
        ['Pre-trained model', 'Remote Storage', pre_trained_model_location_groups['online']],
        ['Self-trained model', 'Repository', self_trained_model_location_groups['file system (saved in VCS)']],
        ['Pre-trained model', 'Repository', pre_trained_model_location_groups['file system (saved in VCS)']],
    ]

    x_label = '# of model files from all repositories'
    y_label = 'Model storage locations'

    plot_data = pd.DataFrame(data, columns=['categories', 'label', 'data'])
    graph_save_file_path = os.path.join(save_root, 'model_location_groups_per_category.pdf')
    plot_multi_bar_and_save(plot_data, x_label, y_label, 'Trained model types', graph_save_file_path)

    unknown_trainer_models_in_repository = unknown_trainer_model_location_groups[
        'file system (saved in VCS)'] if 'file system (saved in VCS)' in unknown_trainer_model_location_groups.keys() else 0
    runtime_unknown_trainer_models = unknown_trainer_model_location_groups['runtime memory'] \
        if 'runtime memory' in unknown_trainer_model_location_groups.keys() else 0

    data = {
        'File System': pre_trained_model_location_groups['file system (not saved in VCS)'] +
                       self_trained_model_location_groups['file system (not saved in VCS)'] +
                       unknown_trainer_model_location_groups['file system (not saved in VCS)'],
        'Remote Storage': pre_trained_model_location_groups['online'] +
                          self_trained_model_location_groups['online'] +
                          unknown_trainer_model_location_groups['online'],
        'Repository': pre_trained_model_location_groups['file system (saved in VCS)'] +
                      self_trained_model_location_groups['file system (saved in VCS)'] +
                      unknown_trainer_models_in_repository,
        'Runtime Memory': runtime_pre_trained_models +
                          runtime_self_trained_models +
                          runtime_unknown_trainer_models,
    }

    plot_data = pd.DataFrame(data.items(), columns=['label', 'data'])
    graph_save_file_path = os.path.join(save_root, 'model_location_groups.pdf')
    plot_groups_and_save(plot_data, x_label, y_label, graph_save_file_path, show_percentage=True)


def plot_model_sizes_per_location_group(models, save_file_path):
    files_with_valid_size = models[(models['model_size'] != '') & (models['model_size'] != 'unknown')]
    files_with_valid_size['model_size'] = files_with_valid_size['model_size'].apply(
        lambda size: float(size.split(' ')[0]))

    remote_file_sizes = files_with_valid_size[files_with_valid_size['model_location'] == 'online'][
        'model_size'].values.tolist()
    print(f'Median remote file size among {len(remote_file_sizes)} files: {statistics.median(remote_file_sizes)}')

    repository_file_sizes = \
        files_with_valid_size[files_with_valid_size['model_location'] == 'file system (saved in VCS)'][
            'model_size'].values.tolist()
    print(
        f'Median repository file size among {len(repository_file_sizes)} files: {statistics.median(repository_file_sizes)}')

    data = [
        ['Remote Storage', remote_file_sizes],
        ['Repository', repository_file_sizes]
    ]
    plot_data = pd.DataFrame(data, columns=['label', 'data'])
    plot_data = plot_data.explode('data')
    plot_data['data'] = plot_data['data'].astype('float')

    plot_file_sizes_per_location_group(plot_data, max(repository_file_sizes), 'Size of model files (in MB)',
                                       'Model storage locations', save_file_path)


def plot_model_categories_distribution(model_files, save_file_path):
    self_pre_trained_model_files, third_party_model_files, unknown_trainer_model_files = get_models_per_category(
        model_files)

    data = {
        'Self-trained': len(self_pre_trained_model_files),
        'Pre-trained': len(third_party_model_files),
        'Unknown trainer': len(unknown_trainer_model_files)
    }
    pprint(data)

    plot_data = pd.DataFrame(data.items(), columns=['label', 'data'])
    plot_data = plot_data.sort_values(by=['data'], ascending=False)

    plot_groups_and_save(plot_data, '# of model files from all repositories', 'Trained model types', save_file_path,
                         figure_height=2.3)


def plot_model_load_purposes(code_segments, save_file_path):
    purpose_mapper = {
        'prediction': 'Inference',
        'evaluation': 'Model Assessment',
        'resume training': 'Resume Training',
        'testing': 'Model Assessment',
        'change data structure of model file': 'Change Data Structure',
        'unknown': 'Unknown Purpose',
        '': 'Unknown Purpose'
    }
    pre_trained_model_load_purposes = code_segments['model_load_purpose'].values.tolist()
    pre_trained_model_load_purposes = [purpose_mapper[purpose] for purpose in pre_trained_model_load_purposes]
    data = dict(collections.Counter(pre_trained_model_load_purposes).most_common())

    plot_data = pd.DataFrame(data.items(), columns=['label', 'data'])
    plot_data = plot_data.sort_values(by=['data'], ascending=False)

    plot_groups_and_save(plot_data, '# of pre-trained model loading code segments',
                         'Model load purposes', save_file_path)


def plot_file_distribution_per_repository(files, save_file_path):
    files_per_repo_count = files.groupby('repository_name').size().values.tolist()
    files_per_repo_count += ([0] * (93 - files['repository_name'].nunique()))

    print(f'Median repo has {statistics.median(files_per_repo_count)} model files')

    plot_one_violin(files_per_repo_count, '# of model files per repository', save_file_path)


def file_storage_distribution_per_repo(model_files, save_file_path):
    files_per_repo_count = model_files.groupby('repository_name').size().to_frame('#_of_files_in_repo')
    repo_names_having_more_than_one_file = files_per_repo_count[files_per_repo_count['#_of_files_in_repo'] > 1].index
    print(f'{len(repo_names_having_more_than_one_file)} repos have more than 1 model file')

    repos_having_more_than_one_file = model_files[
        model_files['repository_name'].isin(repo_names_having_more_than_one_file)]

    locations_per_repo = repos_having_more_than_one_file.groupby(['repository_name'])[
        'model_location'].unique().to_frame('model_locations').reset_index()
    locations_per_repo['#_of_model_locations'] = locations_per_repo['model_locations'].apply(lambda l: len(l))
    print(
        f'Among them, {len(locations_per_repo[locations_per_repo["#_of_model_locations"] == 1])} repos use single storage to store all model files')

    locations_per_repo.to_csv(save_file_path, index=False)


def plot_per_storage_per_repo_files(files, save_file_path):
    storages_per_repo = files.groupby('repository_name')['model_location'].unique().to_frame('model_locations')
    storages = storages_per_repo['model_locations'].explode().tolist()
    storage_dict = dict(collections.Counter(storages))

    data = [
        ['File System', storage_dict['file system (not saved in VCS)']],
        ['Remote Storage', storage_dict['online']],
        ['Repository', storage_dict['file system (saved in VCS)']],
        ['Runtime Memory', storage_dict['runtime memory']],
    ]

    plot_data = pd.DataFrame(data, columns=['label', 'data'])

    plot_groups_and_save(plot_data, '# of repositories using the storage', 'Model storage locations', save_file_path,
                         show_percentage=False)


if __name__ == '__main__':
    model_files = pd.read_csv(paths.MODEL_FILES_FILE, dtype={'model_size': str}, na_filter=False)
    pprint(dict(collections.Counter(model_files['model_location'].values.tolist())))

    model_files['model_location'].replace('file system (not saved in VCS - outside of the repository)',
                                          'file system (not saved in VCS)', regex=False, inplace=True)
    model_files['model_location'].replace('file system (source unknown)',
                                          'file system (not saved in VCS)', regex=False, inplace=True)

    graph_save_root = os.path.join(paths.DATA_DIRECTORY, 'graphs', 'plots_on_model')

    graph_save_file_path = os.path.join(graph_save_root, 'per_storage_per_repo_model_files.pdf')
    plot_per_storage_per_repo_files(model_files, graph_save_file_path)

    graph_save_file_path = os.path.join(graph_save_root, 'model_file_distribution_per_repo.pdf')
    plot_file_distribution_per_repository(model_files, graph_save_file_path)

    file_save_file_path = os.path.join(paths.DATA_DIRECTORY, 'model_storage_locations_per_repo.csv')
    file_storage_distribution_per_repo(model_files, file_save_file_path)

    graph_save_file_path = os.path.join(graph_save_root, 'model_categories_distribution.pdf')
    plot_model_categories_distribution(model_files, graph_save_file_path)

    plot_model_location_groups(model_files, graph_save_root)

    graph_save_file_path = os.path.join(graph_save_root, 'model_sizes_per_location.pdf')
    plot_model_sizes_per_location_group(model_files, graph_save_file_path)

    graph_save_file_path = os.path.join(graph_save_root, 'pre_trained_model_load_purposes.pdf')
    pre_trained_model_load_code_segments = pd.read_csv(
        os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'model_load_analysis_result.csv'), na_filter=False)
    plot_model_load_purposes(pre_trained_model_load_code_segments, graph_save_file_path)
