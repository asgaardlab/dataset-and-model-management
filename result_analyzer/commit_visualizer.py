import ast
import os
from itertools import chain

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from data_analyzer.file_changing_commit_lister import list_file_changing_commits
from util import paths


def get_file_commits_per_repo(file_type):
    number_of_commits = []
    file_path = os.path.join(paths.DATA_DIRECTORY, 'file_path_with_#_of_commits.csv')
    file_with_commits = pd.read_csv(file_path)

    files = file_with_commits[file_with_commits['location_of'] == file_type]
    files['file_changing_commit_hashes'] = files['file_changing_commit_hashes'].apply(ast.literal_eval)
    files_per_repo = files.groupby('repo_name')

    print(file_type, len(files_per_repo))

    for repo_name, files in files_per_repo:
        commit_hashes = set(chain.from_iterable(files['file_changing_commit_hashes']))
        number_of_commits.append([file_type, len(commit_hashes)])
        print(len(commit_hashes), file_type, repo_name)

    return number_of_commits


def plot():
    sns.set_style('white')

    commits_per_repo = get_file_commits_per_repo('dataset')
    commits_per_repo += get_file_commits_per_repo('model')

    plot_data = pd.DataFrame(commits_per_repo, columns=['location_of', '#_of_commits'])

    ax = sns.violinplot(data=plot_data, x='#_of_commits', y='location_of', quartiles=True, cut=0, color='C0')
    sns.despine(ax=ax, top=True, right=True, left=False)

    print('dataset', np.median(plot_data[plot_data['location_of'] == 'dataset']['#_of_commits']))
    print('model', np.median(plot_data[plot_data['location_of'] == 'model']['#_of_commits']))

    ax.set_yticklabels(['Dataset', 'Model'])
    ax.set_ylabel('')
    ax.set_xlabel('# of commits per repository')

    plt.tight_layout()

    plt.savefig(os.path.join(paths.DATA_DIRECTORY, 'graphs', 'commit_distribution_per_repo.pdf'))
    plt.show()


if __name__ == '__main__':
    list_file_changing_commits()
    plot()
