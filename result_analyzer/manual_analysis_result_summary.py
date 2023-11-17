import collections
import os.path
from pprint import pprint

import yaml
from charset_normalizer import detect

from util import paths


def get_models_from_result() -> dict:
    result_dir = os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'selected')
    result_file_names = os.listdir(result_dir)

    all_models = {'training': [], 'pre_trained': []}
    for result_file_name in result_file_names:
        # print(result_file_name)
        with open(os.path.join(result_dir, result_file_name), 'rb') as result_file:
            data = result_file.read()
            encoding = detect(data)['encoding']
            text = data.decode(encoding)

            result = yaml.load(text, Loader=yaml.FullLoader)
            for model_type in result['models'].keys():
                for model in result['models'][model_type]:
                    model['model']['repository_name'] = result['repository_name']
                    model['model']['repository_comment'] = result['comment'] if 'comment' in result.keys() else None
                all_models[model_type] += result['models'][model_type]

    return all_models


def get_pre_trained_models_from_result() -> list:
    return get_models_from_result()['pre_trained']


def get_training_models_from_result() -> list:
    return get_models_from_result()['training']


def parse_result():
    result_dir = os.path.join(paths.MANUAL_ANALYSIS_RESULT_DIRECTORY, 'selected')
    result_file_names = os.listdir(result_dir)

    total_no_of_pre_trained_models = 0
    total_no_of_training_models = 0
    total_repositories_having_instruction_in_readme = 0

    total_no_of_training_provided_dataset = 0
    dataset_provided_location_types = ['online',
                                       'file system (saved in VCS)',
                                       'library dataset',
                                       'runtime memory']

    pre_trained_model_load_purposes = []
    model_locations = []
    dataset_locations = []
    for result_file_name in result_file_names:
        # print(result_file_name)
        with open(os.path.join(result_dir, result_file_name), 'rb') as result_file:
            data = result_file.read()
            encoding = detect(data)['encoding']
            text = data.decode(encoding)

            result = yaml.load(text, Loader=yaml.FullLoader)

            if result['has_instruction_in_readme']:
                total_repositories_having_instruction_in_readme += 1

            models = result['models']

            pre_trained_models = models["pre_trained"] if "pre_trained" in models.keys() else []
            training_models = models["training"] if "training" in models.keys() else []

            total_no_of_pre_trained_models += len(pre_trained_models)
            total_no_of_training_models += len(training_models)

            for index, pre_trained_model in enumerate(pre_trained_models):
                model = pre_trained_model['model']

                # if model['model_load_purpose'] == 'unknown':
                #     print(result_file_name, model['location'])

                pre_trained_model_load_purposes.append(model['model_load_purpose'])
                model_locations.append(model['location_type'])

            for index, training_model in enumerate(training_models):
                dataset = training_model['dataset']

                dataset_locations.append(dataset['location_type'])
                if dataset['location_type'] in dataset_provided_location_types:
                    total_no_of_training_provided_dataset += 1

    print(f'{len(result_file_names)} repositories analyzed')
    print(f'= {total_no_of_pre_trained_models} model loading code')
    print(f'= {total_no_of_training_models} training code')
    print(
        f'\t= {total_no_of_training_provided_dataset} trainings have provided dataset')

    print(f'{total_repositories_having_instruction_in_readme} repositories have instruction in readme file')

    print('Model load purposes:')
    pprint(collections.Counter(pre_trained_model_load_purposes))

    print('Model locations:')
    pprint(collections.Counter(model_locations))

    print('Dataset locations:')
    pprint(collections.Counter(dataset_locations))


if __name__ == '__main__':
    parse_result()
