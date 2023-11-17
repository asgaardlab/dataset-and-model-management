import pandas as pd

from util import paths


def select_repositories_for_manual_analysis():
    repos = pd.read_csv(paths.SELECTED_REPOSITORIES_FILE)
    sample_repos = repos.sample(n=93)

    sample_repos.to_csv(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE)


if __name__ == '__main__':
    select_repositories_for_manual_analysis()
