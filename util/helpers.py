import ast
import glob
import os
import pickle
import string
import time
from _ast import AST
from distutils.core import run_setup
from urllib.parse import urlparse

import charset_normalizer
import nltk as nltk
import pandas as pd
from github import Github, RateLimitExceededException
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet
from packaging.requirements import Requirement
from pandas import DataFrame

from detector.import_finder import ImportFinder
from util import constants, paths

file_open_error_count = 0
setup_file_parse_error_count = 0


def get_ast(file_path: str) -> ast:
    abs_file_path = os.path.abspath(file_path)
    try:
        with open(abs_file_path, 'rb') as opened_file:
            content = opened_file.read()
            encoding = charset_normalizer.detect(content)['encoding']
            content = content.decode(encoding)
            return ast.parse(content)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, SyntaxError) as e:
        global file_open_error_count
        file_open_error_count += 1
        print_error(f'{file_open_error_count}] {e} ({abs_file_path})')
        return None


# copied from requirements-parser library
_UNSUPPORTED_OPTIONS = {
    '-c': 'Unused option -c (constraint). Skipping.',
    '--constraint': 'Unused option -c (constraint). Skipping.',
    '-r': 'Unused option -r (requirement). Skipping.',
    '--requirement': 'Unused option -r (requirement). Skipping.',
    '--no-binary': 'Unused option --no-binary. Skipping',
    '--only-binary': 'Unused option --only-binary. Skipping',
    '--prefer-binary': 'Unused option --prefer-binary. Skipping',
    '--require-hashes': 'Unused option --require-hashes. Skipping',
    '--pre': 'Unused option --pre. Skipping',
    '--trusted-host': 'Unused option --trusted-host. Skipping',
    '--use-feature': 'Unused option --use-feature. Skipping',
    '-Z': 'Unused option -Z (always-unzip). Skipping.',
    '--always-unzip': 'Unused option --always-unzip. Skipping.'
}


# inspired from requirements-parser library
def get_requirement(line):
    line = line.split("#")[0]
    line = line.split("\\")[0]

    line = line.strip()

    if not line or line == '':
        return None
    elif line.startswith('-e') or line.startswith('--editable'):
        return None
    elif line.startswith('-r') or line.startswith('--requirement'):
        return None
    elif line.startswith('--hash'):
        return None
    elif line.startswith('-f') or line.startswith('--find-links') or \
            line.startswith('-i') or line.startswith('--index-url') or \
            line.startswith('--extra-index-url') or \
            line.startswith('--no-index'):
        return None
    else:
        for param in _UNSUPPORTED_OPTIONS.keys():
            if line.startswith(param):
                return None

    try:
        return Requirement(line)
    except Exception as e:
        print(f'\033[91m[{line}: {e}\033[0m')

    return None


def get_requirements_file_paths(data_dir: str) -> DataFrame:
    if os.path.isfile(paths.SAVED_REQUIREMENTS_FILE):
        return pd.read_csv(paths.SAVED_REQUIREMENTS_FILE)

    files = glob.glob(data_dir + '/**/*requirement*.txt', recursive=True)

    file_list = []
    for file in files:
        requirements_file_relative_path = file.split(paths.REPOSITORIES_DIRECTORY, 1)[-1]
        repository_name = get_repo_name_from_dir_name(requirements_file_relative_path.split('\\')[1])
        file_list.append([file, requirements_file_relative_path, repository_name])

    files_df = pd.DataFrame(file_list, columns=['requirements_file_path', 'requirements_file_relative_path',
                                                'repository_name'])
    files_df.to_csv(paths.SAVED_REQUIREMENTS_FILE, index=False)

    return files_df


def get_setup_file_paths(data_dir: str) -> DataFrame:
    if os.path.isfile(paths.SAVED_SETUP_FILE):
        return pd.read_csv(paths.SAVED_SETUP_FILE)

    setup_files = glob.glob(data_dir + '/**/setup.py', recursive=True)
    setup_file_list = []
    for setup_file in setup_files:
        relative_path = setup_file.split(paths.REPOSITORIES_DIRECTORY, 1)[-1]
        repository_name = get_repo_name_from_dir_name(relative_path.split('\\')[1])
        setup_file_list.append([setup_file, relative_path, repository_name])

    files_df = pd.DataFrame(setup_file_list, columns=['setup_file_path', 'relative_file_path', 'repository_name'])
    files_df.to_csv(paths.SAVED_SETUP_FILE, index=False)

    return files_df


def get_repo_name_from_dir_name(directory_name: str):
    repo_name = directory_name.replace('@', '/')
    if repo_name[-1] == "$":
        repo_name = repo_name[:-1] + "."
    return repo_name


def get_dir_name_from_repo_name(repository_name: str):
    dir_name = repository_name.replace('/', '@')
    if dir_name[-1] == ".":
        dir_name = dir_name[:-1] + "$"
    return dir_name


def get_pypi_api_url(package_name):
    return 'https://pypi.org/pypi/' + package_name + '/json'


def print_error(print_line):
    print(f'\033[91m{print_line}\033[0m')


def parse_requirements_file(requirements_file_path):
    results = charset_normalizer.from_path(requirements_file_path)
    return str(results.best()).split('\n')


def parse_setup_file(setup_file_path):
    try:
        setup_args = run_setup(setup_file_path, stop_after='init')
        return setup_args.install_requires
        # setup_args = parsesetup.parse_setup(setup_file_path, trusted=True)
        # return setup_args['install_requires'] \
        #     if 'install_requires' in setup_args and type(setup_args['install_requires']) is list[str] \
        #     else []
    except Exception as e:
        global setup_file_parse_error_count
        setup_file_parse_error_count += 1
        print_error(f'[{setup_file_parse_error_count}] Error in parsing setup file {setup_file_path}: {e}')
        return []


def is_github_url(url):
    return urlparse(url).netloc == 'github.com'


def get_repository_detail(full_name):
    try:
        time.sleep(0.5)
        return Github(constants.GITHUB_ACCESS_TOKEN).get_repo(full_name)
    except RateLimitExceededException:
        time.sleep(60 * 2)
        return get_repository_detail(full_name)
    except Exception as e:
        print(f'Error in receiving {full_name}: {e}')
        return None


lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


def preprocess_text(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))  # remove punctuation
    words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in words]


def preprocess_repo_name(repo_name):
    repo_name = repo_name.lower()
    repo_name_parts = repo_name.replace('-', ' ').replace('_', ' ').replace('.', ' ').split()
    return [lemmatizer.lemmatize(name_part, get_wordnet_pos(name_part)) for name_part in
            repo_name_parts]


def get_py_files_per_repository(data_directory):
    if os.path.isfile(paths.SAVED_PY_FILE):
        with open(paths.SAVED_PY_FILE, 'rb') as f:
            return pickle.load(f)

    repository_directories = os.listdir(data_directory)
    py_files = {}
    for repository_directory in repository_directories:
        repository_directory_path = os.path.join(data_directory, repository_directory)
        py_files[repository_directory] = glob.glob(repository_directory_path + '/**/*.py', recursive=True)

    with open(paths.SAVED_PY_FILE, 'wb') as f:
        pickle.dump(py_files, f)

    return py_files


def associate_parent_with_nodes(code_ast):
    for node in ast.walk(code_ast):
        for child in ast.iter_child_nodes(node):
            child.parent = node


def get_import_node(name: str, before_lineno: int, code_ast: AST) -> tuple[
    (ast.Import, ast.ImportFrom, None), (str, None)]:
    name_parts = name.split('.')
    for i in range(len(name_parts), 0, -1):
        initial_name_part = '.'.join(name_parts[0:i])
        import_finder = ImportFinder(initial_name_part, before_lineno)
        import_finder.visit(code_ast)

        if len(import_finder.import_nodes) > 0:
            return import_finder.import_nodes[-1], initial_name_part
    return None, None


def get_code_lines(file_path: str) -> list[str]:
    with open(file_path, 'rb') as file:
        return [line.decode(charset_normalizer.detect(line)['encoding']) for line in file.readlines()]


def get_repository_name_from_file_path(file_path: str) -> str:
    requirements_file_relative_path = file_path.split(paths.WORKING_REPOSITORIES_DIRECTORY, 1)[-1]
    return get_repo_name_from_dir_name(requirements_file_relative_path.split('\\')[1])


def get_relative_path_from_file_path(file_path: str) -> str:
    file_relative_path = file_path.split(paths.WORKING_REPOSITORIES_DIRECTORY, 1)[-1]
    return '/'.join(file_relative_path.split('\\')[2:])


def create_directory_if_not_exists(directory_path):
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
