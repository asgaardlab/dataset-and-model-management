import os
from itertools import chain

import pandas as pd

from result_analyzer.manual_analysis_result_summary import get_models_from_result
from util import paths


def export_dataset_analysis_result(training_models) -> pd.DataFrame:
    result = []
    for trained_model in training_models:
        dataset = trained_model['dataset']

        comment = dataset['comment'] if 'comment' in dataset.keys() else None
        dataset_path_set_from = dataset['location_set_from'] if 'location_set_from' in dataset.keys() else None
        result.append([trained_model['model']['repository_name'], trained_model['model']['repository_comment'],
                       dataset['location'], dataset['location_type'], dataset_path_set_from, dataset['size'], comment])

    dataset_analysis_result = pd.DataFrame(result, columns=['repository_name', 'repository_comment', 'dataset_path',
                                                            'dataset_location', 'dataset_path_set_from', 'dataset_size',
                                                            'comment'])
    dataset_analysis_result.to_csv(os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'dataset_analysis_result.csv'))

    return dataset_analysis_result


def export_model_train_result(training_models) -> pd.DataFrame:
    result = []
    for trained_model in training_models:
        model = trained_model['model']

        comment = model['comment'] if 'comment' in model.keys() else None
        is_fine_tuned = model['is_resume_from_checkpoint'] if 'is_resume_from_checkpoint' in model.keys() else None
        foundation_model_location = model[
            'resume_from_checkpoint_location_type'] if 'resume_from_checkpoint_location_type' in model.keys() else None
        result.append(
            [trained_model['model']['repository_name'], trained_model['model']['repository_comment'], is_fine_tuned,
             foundation_model_location, model['save_location'], comment])

    model_train_analysis_result = pd.DataFrame(result,
                                               columns=['repository_name', 'repository_comment', 'is_fine_tuned',
                                                        'foundation_model_location', 'model_save_path', 'comment'])
    model_train_analysis_result.to_csv(
        os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'model_train_analysis_result.csv'))

    return model_train_analysis_result


def export_model_load_result(pre_trained_models) -> pd.DataFrame:
    result = []
    for pre_trained_model in pre_trained_models:
        model = pre_trained_model['model']

        comment = model['comment'] if 'comment' in model.keys() else None
        model_path_set_from = model['location_set_from'] if 'location_set_from' in model.keys() else None
        result.append(
            [model['repository_name'], model['repository_comment'], model['self_trained'], model['model_load_purpose'],
             model['location'], model['location_type'], model_path_set_from, model['size'], comment])

    model_load_analysis_result = pd.DataFrame(result, columns=['repository_name', 'repository_comment',
                                                               'is_self_pre_trained', 'model_load_purpose',
                                                               'model_path', 'model_location',
                                                               'model_path_set_from', 'model_size', 'comment'])
    model_load_analysis_result.to_csv(
        os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'model_load_analysis_result.csv'))

    return model_load_analysis_result


def get_pre_trained_model_files(models):
    pre_trained_models = export_model_load_result(models)
    models_per_repo = pre_trained_models.groupby(['repository_name', 'model_path'])

    files = []
    for name_of_the_group, group in models_per_repo:
        files.append([name_of_the_group[0], group['is_self_pre_trained'].iloc[0], name_of_the_group[1], len(group),
                      group['model_location'].iloc[0], group['model_path_set_from'].iloc[0],
                      group['model_size'].iloc[0], group['comment'].iloc[0]])

    print(f'{len(files)} model files')
    pd.DataFrame(files,
                 columns=['repository_name', 'is_self_pre_trained', 'model_path', 'files_count', 'model_location',
                          'model_path_set_from', 'model_size', 'comment']).to_csv(paths.MODEL_FILES_FILE, index=False)


def get_dataset_files(models):
    training_datasets = export_dataset_analysis_result(models)
    datasets_per_repo = training_datasets.groupby(['repository_name', 'dataset_path'])

    files = []
    for name_of_the_group, group in datasets_per_repo:
        not_none_comments = set(group[group['comment'].notnull()]['comment'].values.tolist())
        comments = list(not_none_comments)
        files.append([name_of_the_group[0], name_of_the_group[1], len(group), group['dataset_location'].iloc[0],
                      group['dataset_path_set_from'].iloc[0], group['dataset_size'].iloc[0], comments])

    print(f'{len(files)} dataset files')
    pd.DataFrame(files,
                 columns=['repository_name', 'dataset_path', 'files_count', 'dataset_location', 'dataset_path_set_from',
                          'dataset_size', 'comments']).to_csv(paths.DATASET_FILES_FILE, index=False)


def export_manual_analysis_result():
    models = get_models_from_result()

    export_dataset_analysis_result(models['training'])
    export_model_train_result(models['training'])
    export_model_load_result(models['pre_trained'])


def export_dataset_and_model_files():
    models = get_models_from_result()

    get_dataset_files(models['training'])
    get_pre_trained_model_files(models['pre_trained'])


if __name__ == '__main__':
    export_manual_analysis_result()
    export_dataset_and_model_files()
